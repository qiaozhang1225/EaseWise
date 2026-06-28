# Local Change Summary - Post Export 7 Four Pillars Sync

## Baseline

- Last AI Studio export cycle: `20260625-170000-export-7-four-pillars-shensha-merge`
- Last AI Studio zip SHA256: `4059a24cc34a20e6e5e356701529d78ce5be05671ae477902487e606d2b8fd7c`
- Local baseline ref after export 7 archive: `eac3f4e`
- Current local HEAD: `897d3c1`
- Current dirty local file: `product/frontend/src/components/four-pillars/FourPillarsAnalysis.vue`

## Scope Since Export 7

Local development has moved beyond AI Studio export 7 in five related areas:

1. Four Pillars input engine:
   - Professional compact input layout.
   - Bottom-sheet date and location drawers.
   - Solar/lunar wheel selectors.
   - Manual numeric hand-fill fields for year/month/day/hour/minute.
   - True solar time preview and birth-location support.

2. Four Pillars generation flow:
   - Waiting animation begins immediately after submit intent.
   - The polling flow no longer waits for full LLM completion if a renderable chart is already available.
   - Result page is shown when `chart_display.pillars` or `chart.pillars` has the four pillars.

3. Four Pillars result page:
   - Compact chart header.
   - `更多命盘信息` centered modal.
   - Five-element progress bars.
   - Yuan Tiangang bone-weight display, including total weight, parts, fate pattern, and verse.

4. Entry page consistency:
   - Phone QiMen and Four Pillars input pages use the same compact function-title card.
   - Both use the animated dot, translucent corner mark, 16px title, and unified CTA copy.

5. Backend knowledge and mock-data requirements:
   - Added structured birth-location data.
   - Added true solar time calculation module.
   - Added Yuan Tiangang bone-weight structured table and calculation.
   - Expanded `chart_display.profile` fields consumed by the frontend.

## Local Commit Range

```text
897d3c1 fix: show four pillars chart before full render completes
42bbc54 fix: stabilize four pillars input and waiting flow
fb978ce feat: refine four pillars frontend experience
cdbafa6 feat: expand four pillars birth input engine
```

## Main Changed Files

```text
features/four_pillars/engine/bone_weight.py
features/four_pillars/engine/service.py
features/four_pillars/engine/solar_time.py
features/four_pillars/engine/tests/test_bone_weight.py
features/four_pillars/knowledge/explicit-knowledge.md
features/four_pillars/knowledge/shared/interpretation-boundaries.md
features/four_pillars/knowledge/structured/birth-locations.json
features/four_pillars/knowledge/structured/yuan-tiangang-bone-weight.json
features/four_pillars/tools/build_birth_locations.py
product/frontend/src/components/analysis/Analysis.vue
product/frontend/src/components/four-pillars/FourPillarsAnalysis.vue
product/frontend/src/components/four-pillars/FourPillarsNatalTable.vue
product/frontend/src/lib/api.ts
product/frontend/src/types/api.ts
```

## Current Dirty Diff

The latest uncommitted local change adds pure manual numeric hand-fill inputs above the date wheels:

- Solar mode: `year`, `month`, `day`, `hour`, `minute`.
- Lunar mode: `year`, `month`, `day`, `hour`, `minute`.
- No browser-native `date` or `time` input is used.
- Manual values call `setSolarPart` or `setLunarPart`, clamp ranges, and sync wheel selection.

This is a product correction after the user rejected native date/time inputs.

## Verification Already Run

```text
npm run lint
npm run build
```

Both passed after the manual numeric input change. Vite produced only the existing chunk-size warning.
