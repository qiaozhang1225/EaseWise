# Local Merge Plan - Export 9 Homepage Layout

## Summary

Export 9 should be treated primarily as homepage design input. The useful part is the unified entry-card layout for three primary functions, two secondary tools, and four upcoming placeholders.

The Meihua page is a prototype and should not be imported as production logic without a feature plan.

## Proposed Merge Scope

### Include

- `product/frontend/src/components/home/Home.vue`
  - Port the left-icon horizontal-flow card design.
  - Add third primary card for `梅花易数评测`.
  - Keep 三大主推功能 as vertical full-width cards.
  - Keep 黄历查询 and 五行属性 as secondary two-column buttons.
  - Add four upcoming disabled placeholders.
  - Preserve local `useEaseWiseApp` data sources and event boundaries.

- `product/frontend/src/index.css`
  - Add only the two animation classes:
    - `bazi-float`
    - `meihua-sway`

### Decide Before Include

- `product/frontend/src/App.vue`
  - If Meihua should be clickable now, add route/tab and auth gate.
  - If not, leave the Meihua card disabled or show a toast.

- `product/frontend/src/components/meihua/MeihuaAnalysis.vue`
  - If used now, mark it clearly as prototype and keep it behind a feature flag.
  - For production, replace with a backend-backed feature later.

### Exclude

- `server.ts`
- `src/components/four-pillars/mockLocations.ts`
- AI Studio modifications to `FourPillarsAnalysis.vue`

## Required Local Behavior Preservation

- Keep existing auth modal and registered-user gate for live paid features.
- Keep existing phone and Four Pillars routes.
- Keep Four Pillars location picker and true-solar-time implementation untouched.
- Keep local runtime-config pricing as source of truth.
- Do not invent Meihua pricing in local runtime unless product decides it.

## Open Product Decision

Before implementation, clarify whether `梅花易数` should be:

1. **Clickable prototype now**: show AI Studio-style Meihua page behind registered-user gate.
2. **Homepage placeholder now**: visible card but disabled/upcoming until backend feature is ready.
3. **Clickable but no deduction**: route opens a preview page, clearly marked as preview.

Given current production discipline, recommended path is option 2 unless the user explicitly wants a live prototype route.

## Test Plan If Implemented

- `npm run lint`
- `npm run build`
- Browser check:
  - Home shows three primary full-width cards.
  - Yellow/blue palette remains consistent.
  - Phone card still navigates to phone review.
  - Four Pillars card still navigates to Bazi review.
  - Meihua behavior matches the product decision.
  - 黄历查询 scrolls to the almanac area or otherwise gives a clear action.
  - 五行属性 shows current unavailable/planning state.
  - Upcoming placeholders are visibly disabled and not clickable.
