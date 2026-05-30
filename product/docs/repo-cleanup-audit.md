# EaseWise Repo Cleanup Audit

Last updated: 2026-05-27

## Active Paths

- `product/backend/api/routers/phone_qimen.py` routes phone review requests.
- `features/phone_qimen/rendering` owns phone summary, phone stability, and aspect LLM rendering.
- `features/phone_qimen/knowledge/loader.py` exposes `phone_summary`, `stability`, and `sections/aspects/*`.
- `features/phone_qimen/scoring/total_score` owns the total score, board facts, score template, and bundle output.
- `features/phone_qimen/scoring/dimensions` owns the product-facing dimension scores and stability dimension score.

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

- `features/phone_qimen/scoring/total_score/engine.py` is the deterministic board and total-score builder.
- `features/phone_qimen/scoring/total_score/score_facts.py` builds the factual payload used by the phone summary.
- `features/phone_qimen/scoring/total_score/score_template.py` builds the persisted `score_template`.
- `features/phone_qimen/scoring/total_score/bundle.py` packages `score_result` and `score_template`.
- `features/phone_qimen/scoring/dimensions/stability.py` is still used by stability rendering and persisted-review compatibility.
- `features/phone_qimen/scoring/dimensions/engine.py` is the active product-facing dimension scorer.

This pass removed the old `dimension_score_v2`, `dimension_score_v3`, and
`total_score_v2` public package names from the active tree. It also removed the
active `payloads`, `services`, `types`, `template_parts`, root `engine.py`, and
`aspects_v2` layers.

## Next Cleanup Candidates

- Replace direct dependence on the old stability dimension shape after downstream callers stop reading `stability_dimension_score`.
- Delete archived compatibility wrappers after one stabilization window if no external tool imports them.
