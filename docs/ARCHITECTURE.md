# WatchTower Architecture

WatchTower is a public, sanitized demonstration of a reference-free Korean-to-English machine-translation quality evaluation and selective post-editing workflow.

This document describes the public demo only. It does not reproduce proprietary production code, private datasets, internal deployment details, or non-public evaluation reports.

## Pipeline

```text
Source text + machine translation
        |
        v
+------------------------------+
| Reference-free evaluation    |
| - LaBSE semantic similarity  |
| - COMET quality estimation   |
| - GEMBA-style LLM assessment |
+------------------------------+
        |
        v
+------------------------------+
| Composite Q-Score            |
| normalized quality signals   |
+------------------------------+
        |
        v
+------------------------------+
| Quality classification       |
| + deterministic validation   |
+------------------------------+
        |
        v
+------------------------------+
| Selective post-editing       |
| lower-quality records only   |
+------------------------------+
        |
        v
+------------------------------+
| Re-evaluate edited output    |
+------------------------------+
        |
        v
Human review / final decision
```

## Components

- `filter.py` computes LaBSE cosine similarity and COMET scores, then attaches deterministic validation signals.
- `gemba_batch.py` performs a batched LLM-based assessment of adequacy and fluency.
- `q_score.py` standardizes the quality signals, computes a composite score, and assigns demo quality classes.
- `ape.py` post-edits records that need improvement and re-evaluates the edited text.
- `validation.py` checks terminology, placeholders, technical identifiers, and coarse length consistency.
- `run_pipeline.py` orchestrates the three stages and writes outputs into a versioned run directory.

## Public-demo configuration

The numerical defaults in this repository exist only to make the demo runnable and understandable. They should not be interpreted as a disclosure of proprietary production tuning or as a published research benchmark. All main models and scoring parameters can be overridden through environment variables or `cfg.py`.

## Design principle

The system is designed to prioritize human attention rather than replace human review. Automated quality signals identify records that deserve more attention; selective post-editing proposes corrections; the final decision remains with a reviewer.
