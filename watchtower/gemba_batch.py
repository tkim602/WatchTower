from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

import cfg
from q_score import score_records

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_prompt(src: str, mt: str, validation: dict) -> str:
    return f"""You are a Korean-to-English translation quality assessor.
Evaluate adequacy and fluency from 0 to 100.
Return JSON only with keys: overall, adequacy, fluency, evidence.
Keep the evidence concise.

Source: {src}
Translation: {mt}
Validation context: {json.dumps(validation, ensure_ascii=False)}
"""


async def evaluate_one(record: dict) -> dict:
    response = await client.chat.completions.create(
        model=cfg.GEMBA_MODEL,
        temperature=0,
        messages=[{"role": "user", "content": build_prompt(record["src"], record["mt"], record["validation"])}],
        response_format={"type": "json_object"},
    )
    parsed = json.loads(response.choices[0].message.content)
    row = dict(record)
    row["gemba"] = float(parsed.get("overall", 0))
    row["gemba_adequacy"] = float(parsed.get("adequacy", 0))
    row["gemba_fluency"] = float(parsed.get("fluency", 0))
    row["gemba_evidence"] = str(parsed.get("evidence", ""))
    return row


async def main() -> None:
    run_dir = Path(os.getenv("RUN_DIR", cfg.OUT_DIR))
    rows = json.loads((run_dir / cfg.FILTER_OUTPUT_FILENAME).read_text(encoding="utf-8"))

    semaphore = asyncio.Semaphore(cfg.GEMBA_BATCH)

    async def guarded(row: dict) -> dict:
        async with semaphore:
            return await evaluate_one(row)

    evaluated = await asyncio.gather(*(guarded(row) for row in rows))
    scored = score_records(evaluated)

    out = run_dir / cfg.GEMBA_OUTPUT_FILENAME
    out.write_text(json.dumps(scored, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    asyncio.run(main())
