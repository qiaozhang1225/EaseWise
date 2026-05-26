# Archived unused v1 assets

Archived on 2026-05-27 after the phone-review flow moved to:

- `knowledge/sections/phone_summary`
- `knowledge/sections/stability`
- `knowledge/sections/aspects`
- `product/backend/phone_summary`
- `product/backend/stability`
- `product/backend/aspects_v2`
- `scoring/total_score_v2`
- `scoring/dimension_score_v3`

This folder keeps old modules and knowledge packs that are no longer part of the
active product path. They are intentionally archived instead of deleted so they
can still be inspected or restored during the stabilization period.

## Contents

- `knowledge/aspects/`: old aspect knowledge packs for the previous aspect set.
- `knowledge/sections/board_description/`: old board-description knowledge.
- `product/backend/*/rendering.py`: old section-specific LLM renderers replaced
  by the new summary, stability and 12-aspect renderers.
- `local-test-output/tmp/`: local JSON test outputs generated during iteration.

## Not Archived Yet

The old scoring template and payload modules under `scoring/payloads` still
feed parts of the active `score_template`, especially board facts, structure,
four-harms checks and legacy persisted-review compatibility. They should only be
archived after `build_scoring_bundle` is replaced by a lean v2 template builder.
