# AI Studio Export 9 Audit - Homepage Layout And Meihua Entry

## Source

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (9).zip`
- SHA256: `5b39151b0083600cef7e571fed444827d2938ec96f2ff31b57f05fb8169bb177`
- Registered local cache cycle: `.aistudio-sync/cycles/20260627-092903-export-9-home-layout-meihua-entry`

## Files Changed In Export 9

Added:

```text
src/components/four-pillars/mockLocations.ts
src/components/meihua/MeihuaAnalysis.vue
```

Changed:

```text
server.ts
src/App.vue
src/components/four-pillars/FourPillarsAnalysis.vue
src/components/home/Home.vue
src/index.css
```

## What Looks Valuable

### Homepage Entry Layout

`src/components/home/Home.vue` is the main useful design output.

Strong ideas:

- Three primary vertical cards:
  - 数字奇门手机号评测
  - 四柱八字评测
  - 梅花易数评测
- Consistent 106px card height.
- Left-side animated icon.
- Middle title and description.
- Right-bottom action cue, e.g. `立即评测 →`, `立即起卦 →`.
- Embedded small cost badge next to the primary title.
- Secondary two-column buttons for 黄历查询 and 五行属性.
- Four upcoming placeholders with greyed disabled treatment.
- Overall palette stays close to current blue/indigo brand system.

### Animations

`src/index.css` adds:

```css
.bazi-float
.meihua-sway
```

These are small and low-risk design enhancements if imported carefully.

### Meihua Prototype As Design Reference

`src/components/meihua/MeihuaAnalysis.vue` is useful as a product/design prototype:

- Supports 报数起卦, 汉字起卦, 时间起卦.
- Shows 本卦 / 互卦 / 变卦.
- Shows 体卦 / 用卦 and five-element relationship.
- Has a mobile result-page direction that can inform the formal Meihua module.

## Risks And Non-Import Areas

### Do Not Directly Import Meihua Business Logic

`MeihuaAnalysis.vue` is a frontend-only prototype. It contains:

- Large inline trigram and hexagram data.
- A manually curated stroke-count fallback table.
- Direct `fetch('/api/v1/agent/chat')` call for interpretation.
- No local formal points ledger, review history, persistence, runtime-config pricing, or backend-generated report contract.

For local production, Meihua should be implemented as a proper feature module with:

- backend API contract,
- points deduction,
- review record,
- saved history,
- knowledge boundary,
- deterministic calculation service,
- LLM rendering/prompt boundaries.

### App.vue Needs Careful Merge

Export 9 adds:

```ts
type AppTab = 'home' | 'phone' | 'bazi' | 'meihua' | ...
```

and a `handleMeihuaClick()` route. This should only be merged if local product accepts a preview Meihua page now. Otherwise, keep the Home entry as upcoming/non-clickable or behind a feature flag.

### FourPillarsAnalysis And mockLocations

Export 9 includes `src/components/four-pillars/mockLocations.ts` and changes `FourPillarsAnalysis.vue`. This overlaps with the previous picker work. Since the user specifically said this export is mostly about homepage layout, do not merge these Four Pillars picker changes blindly.

Local already has a real structured location dataset and endpoint. AI Studio mock locations should not replace local data flow.

## Recommended Treatment

### Safe To Merge As Design

- Homepage card layout from `Home.vue`.
- `bazi-float` animation.
- `meihua-sway` animation.
- Four upcoming disabled placeholders.

### Merge Only With Product Decision

- `meihua` route in `App.vue`.
- `MeihuaAnalysis.vue`.
- Auth gate for Meihua.
- Any live click behavior for Meihua.

### Do Not Merge

- AI Studio `server.ts` business assumptions.
- `mockLocations.ts` into local runtime.
- Four Pillars picker changes from export 9 unless separately audited against the local picker branch.

## Suggested Next Step

If the user wants to sync this back locally, implement a narrow local merge:

1. Update local `Home.vue` to the export 9 homepage entry design.
2. Add `bazi-float` and `meihua-sway` CSS only.
3. Add Meihua card as either:
   - clickable prototype route, if accepted, or
   - disabled/upcoming card, if backend product is not ready.
4. Keep local Four Pillars picker and location data untouched.
5. Do not import `MeihuaAnalysis.vue` as production logic until product/backend plan is approved.
