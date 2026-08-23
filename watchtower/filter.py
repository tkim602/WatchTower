from __future__ import annotations

import json
import os
import random
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from comet import download_model, load_from_checkpoint

import cfg
from validation import run_all_validations


def load_json(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    random.seed(cfg.SEED)
    np.random.seed(cfg.SEED)

    src_map = load_json(cfg.KO_JSON)
    mt_map = load_json(cfg.EN_JSON)
    termbase = load_json(cfg.TERMBASE_PATH) if cfg.TERMBASE_PATH.exists() else {}

    keys = list(src_map.keys())
    if cfg.LIMIT:
        keys = keys[: min(cfg.LIMIT, len(keys))]

    src = [src_map[k] for k in keys]
    mt = [mt_map.get(k, "") for k in keys]

    cos_model = SentenceTransformer(cfg.COS_MODEL)
    e_src = cos_model.encode(src, normalize_embeddings=True)
    e_mt = cos_model.encode(mt, normalize_embeddings=True)
    cos = (e_src * e_mt).sum(axis=1)

    comet = load_from_checkpoint(download_model(cfg.COMET_MODEL))
    comet_rows = [{"src": s, "mt": t} for s, t in zip(src, mt)]
    comet_scores = comet.predict(comet_rows, batch_size=32)["scores"]

    records = []
    for key, s, t, c, q in zip(keys, src, mt, cos, comet_scores):
        records.append(
            {
                "key": key,
                "src": s,
                "mt": t,
                "cos": float(c),
                "comet": float(q),
                "validation": run_all_validations(s, t, termbase),
            }
        )

    run_dir = Path(os.getenv("RUN_DIR", cfg.OUT_DIR))
    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / cfg.FILTER_OUTPUT_FILENAME
    out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
