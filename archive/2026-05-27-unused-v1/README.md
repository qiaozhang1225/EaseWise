# Archived unused v1 assets

Archived on 2026-05-27 after the phone-review flow moved to:

- `knowledge/sections/phone_summary`
- `knowledge/sections/stability`
- `knowledge/sections/aspects`
- `product/backend/phone_summary`
- `product/backend/stability`
- `product/backend/aspects`
- `scoring/total_score`
- `scoring/dimensions`

This folder keeps old modules and knowledge packs that are no longer part of the
active product path. They are intentionally archived instead of deleted so they
can still be inspected or restored during the stabilization period.

## Contents

- `knowledge/aspects/`: old aspect knowledge packs for the previous aspect set.
- `knowledge/sections/board_description/`: old board-description knowledge.
- `product/backend/*/rendering.py`: old section-specific LLM renderers replaced
  by the new summary, stability and 12-aspect renderers.
- `product/backend/aspects_v2/`: old versioned aspect renderer.
- `scoring/template_parts/`: old payload/template builders.
- `scoring/compat_wrappers/`: old top-level compatibility wrappers.
- `scoring/experimental_total_score/`: archived experimental parallel total-score engine.

## Removed From Archive

Local JSON outputs generated during iteration were removed from the repository
because they are not runtime dependencies and do not carry product knowledge.
