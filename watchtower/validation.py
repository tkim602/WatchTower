import re
from typing import Any, Dict


def check_term_consistency(src: str, mt: str, termbase: dict[str, str]) -> Dict[str, Any]:
    mismatches = []
    for ko_term, en_term in (termbase or {}).items():
        if ko_term.lower() in src.lower() and en_term.lower() not in mt.lower():
            mismatches.append({"src_term": ko_term, "expected_mt": en_term})
    return {
        "score": 1.0 if not mismatches else max(0.0, 1.0 - 0.2 * len(mismatches)),
        "mismatches": mismatches,
    }


def check_placeholders(src: str, mt: str) -> Dict[str, Any]:
    pattern = r"\{\{[^{}]+\}\}"
    src_items = sorted(re.findall(pattern, src))
    mt_items = sorted(re.findall(pattern, mt))
    return {"passed": src_items == mt_items, "source": src_items, "translation": mt_items}


def check_technical_formats(src: str, mt: str) -> Dict[str, Any]:
    patterns = {
        "version": r"\b[vV]?\d+\.\d+(?:\.\d+)?\b",
        "identifier": r"\b(?:HTTP|CVE|SSL|TLS|SPDX)\s*[-:]?\s*[\w.-]+\b",
    }
    issues = []
    for name, pattern in patterns.items():
        a = set(re.findall(pattern, src, flags=re.IGNORECASE))
        b = set(re.findall(pattern, mt, flags=re.IGNORECASE))
        if a != b:
            issues.append(f"{name} mismatch")
    return {"passed": not issues, "issues": issues, "score": 1.0 if not issues else 0.5}


def check_length(src: str, mt: str) -> Dict[str, Any]:
    if not src.strip():
        return {"score": 0.0, "ratio": 0.0, "issue": "empty source"}
    ratio = len(mt.strip()) / len(src.strip())
    if ratio < 0.5 or ratio > 4.0:
        return {"score": 0.3, "ratio": ratio, "issue": "suspicious length ratio"}
    return {"score": 1.0, "ratio": ratio, "issue": None}


def run_all_validations(src: str, mt: str, termbase: dict[str, str] | None = None) -> Dict[str, Any]:
    result = {
        "term_consistency": check_term_consistency(src, mt, termbase or {}),
        "placeholder_check": check_placeholders(src, mt),
        "technical_formats": check_technical_formats(src, mt),
        "length_consistency": check_length(src, mt),
    }
    scores = [
        result["term_consistency"]["score"],
        1.0 if result["placeholder_check"]["passed"] else 0.0,
        result["technical_formats"]["score"],
        result["length_consistency"]["score"],
    ]
    result["overall_score"] = sum(scores) / len(scores)
    return result
