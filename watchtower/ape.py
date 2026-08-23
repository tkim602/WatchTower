from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

import cfg

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_prompt(tag: str) -> str:
    name = "sparrow_fail.txt" if tag == "fail" else "sparrow_soft_pass.txt"
    path = Path(__file__).resolve().parent / "prompts" / "sparrow" / name
    return path.read_text(encoding="utf-8")


async def edit_one(row: dict, termbase: dict[str, str]) -> dict:
    template = load_prompt(row["tag"])
    prompt = template.replace("{TERM}", json.dumps(termbase, ensure_ascii=False)).replace(
        "{EVIDENCE}", row.get("gemba_evidence", "")
    )
    prompt += f"\n\nSRC (ko): {row['src']}\nMT (en): {row['mt']}"

    response = await client.chat.completions.create(
        model=cfg.APE_MODEL,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )

    out = dict(row)
    out["ape"] = response.choices[0].message.content.strip()
    return out


async def main() -> None:
    run_dir = Path(os.getenv("RUN_DIR", cfg.OUT_DIR))
    rows = json.loads((run_dir / cfg.GEMBA_OUTPUT_FILENAME).read_text(encoding="utf-8"))
    termbase = {}
    if cfg.TERMBASE_PATH.exists():
        termbase = json.loads(cfg.TERMBASE_PATH.read_text(encoding="utf-8"))

    semaphore = asyncio.Semaphore(cfg.APE_CONCURRENCY)

    async def maybe_edit(row: dict) -> dict:
        if row.get("tag") == "strict_pass":
            return row
        async with semaphore:
            return await edit_one(row, termbase)

    edited = await asyncio.gather(*(maybe_edit(row) for row in rows))
    out = run_dir / cfg.APE_OUTPUT_FILENAME
    out.write_text(json.dumps(edited, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    asyncio.run(main())
