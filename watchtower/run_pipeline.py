from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path

import cfg


class PipelineRunner:
    def __init__(self) -> None:
        self.code_dir = Path(__file__).resolve().parent
        self.run_dir: Path | None = None

    def create_run_dir(self) -> Path:
        cfg.OUT_DIR.mkdir(parents=True, exist_ok=True)
        i = 1
        while (cfg.OUT_DIR / f"v{i}").exists():
            i += 1
        self.run_dir = cfg.OUT_DIR / f"v{i}"
        self.run_dir.mkdir()
        os.environ["RUN_DIR"] = str(self.run_dir)
        return self.run_dir

    def run_sync(self, name: str) -> None:
        subprocess.run([sys.executable, str(self.code_dir / name)], cwd=self.code_dir, check=True)

    async def run_async(self, name: str) -> None:
        proc = await asyncio.create_subprocess_exec(sys.executable, str(self.code_dir / name), cwd=self.code_dir)
        code = await proc.wait()
        if code:
            raise RuntimeError(f"{name} failed with exit code {code}")

    async def run(self) -> Path:
        run_dir = self.create_run_dir()
        print(f"Run directory: {run_dir}")
        self.run_sync("filter.py")
        await self.run_async("gemba_batch.py")
        await self.run_async("ape.py")
        print(f"Done: {run_dir / cfg.APE_OUTPUT_FILENAME}")
        return run_dir


if __name__ == "__main__":
    asyncio.run(PipelineRunner().run())
