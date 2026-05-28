# EaseWise Repo Cleanup Audit

Last updated: 2026-05-27

## Active Paths

- `product/backend/api/main.py` builds and refreshes phone reviews through `score_phone`, `build_scoring_bundle`, `dimension_score`, `stability_dimension_score`, and the product renderers.
- `product/backend/phone_summary`, `product/backend/stability`, and `product/backend/aspects` are the active LLM rendering paths.
- `knowledge/loader.py` only exposes `phone_summary`, `stability`, and `sections/aspects/*`.
- `scoring/total_score` owns the total score, board facts, score template, and bundle output.
- `scoring/dimensions` owns the product-facing dimension scores and stability dimension score.

## Archived This Pass

- `scoring/bundle_service.py`
- `scoring/personality_payload.py`
- `scoring/skill_bridge.py`
- `scoring/payloads/*`
- `product/backend/aspects_v2`

These were legacy payload builders or compatibility wrappers with no active repository imports. They now live under `archive/2026-05-27-unused-v1/`.

## Already Archived

- Old aspect knowledge packs: `archive/2026-05-27-unused-v1/knowledge/aspects/`
- Old board-description knowledge: `archive/2026-05-27-unused-v1/knowledge/sections/board_description/`
- Old section-specific renderers: `archive/2026-05-27-unused-v1/product/backend/*/`

## Removed

- `archive/2026-05-27-unused-v1/local-test-output/`

The removed files were local JSON iteration outputs, not runtime fixtures or product knowledge.

## Current Scoring Shape

- `scoring/total_score/engine.py` is the deterministic board and total-score builder.
- `scoring/total_score/score_facts.py` builds the factual payload used by the phone summary.
- `scoring/total_score/score_template.py` builds the persisted `score_template`.
- `scoring/total_score/bundle.py` packages `score_result` and `score_template`.
- `scoring/dimensions/stability.py` is still used by stability rendering and persisted-review compatibility.
- `scoring/dimensions/engine.py` is the active product-facing dimension scorer.

This pass removed the old `dimension_score_v2`, `dimension_score_v3`, and
`total_score_v2` public package names from the active tree. It also removed the
active `payloads`, `services`, `types`, `template_parts`, root `engine.py`, and
`aspects_v2` layers.

## Next Cleanup Candidates

- Replace direct dependence on the old stability dimension shape after downstream callers stop reading `stability_dimension_score`.
- Delete archived compatibility wrappers after one stabilization window if no external tool imports them.
