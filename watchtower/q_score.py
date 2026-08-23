from __future__ import annotations

from typing import Iterable
import numpy as np

import cfg


def _mean_std(values: Iterable[float]) -> tuple[float, float]:
    arr = np.asarray(list(values), dtype=float)
    mean = float(arr.mean()) if len(arr) else 0.0
    std = float(arr.std()) if len(arr) else 1.0
    return mean, std or 1.0


def z(value: float, mean: float, std: float) -> float:
    return (float(value) - mean) / std


def score_records(records: list[dict]) -> list[dict]:
    """Apply the public-demo composite Q-Score to evaluated records."""
    stats = {}
    for field in ("cos", "comet", "gemba"):
        stats[field] = _mean_std(r[field] for r in records)

    weights = cfg.Q_SCORE_WEIGHTS
    out = []
    for record in records:
        z_cos = z(record["cos"], *stats["cos"])
        z_comet = z(record["comet"], *stats["comet"])
        z_gemba = z(record["gemba"], *stats["gemba"])
        q = (
            weights["cos"] * z_cos
            + weights["comet"] * z_comet
            + weights["gemba"] * z_gemba
        )

        if q < cfg.Q_SCORE_THRESHOLDS["fail"]:
            tag = "fail"
        elif q < cfg.Q_SCORE_THRESHOLDS["soft_pass"]:
            tag = "soft_pass"
        else:
            tag = "strict_pass"

        row = dict(record)
        row.update({"z_cos": z_cos, "z_comet": z_comet, "z_gemba": z_gemba, "q_score": q, "tag": tag})
        out.append(row)
    return out
