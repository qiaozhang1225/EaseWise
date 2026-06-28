# Local Merge Verification - Export 9 Homepage And Meihua Prototype

## Applied Scope

Merged export 9 design ideas into local frontend:

- Added `meihua` tab routing in `product/frontend/src/App.vue`.
- Added homepage Meihua entry and unified entry-card layout in `product/frontend/src/components/home/Home.vue`.
- Added `product/frontend/src/components/meihua/MeihuaAnalysis.vue` as a frontend design prototype.
- Added Bazi and Meihua icon animations in `product/frontend/src/index.css`.

## Preserved Boundaries

- Did not merge AI Studio `server.ts`.
- Did not merge `src/components/four-pillars/mockLocations.ts`.
- Did not replace local Four Pillars picker, true solar time, or structured location API flow.
- Did not add production Meihua backend, points deduction, history, or report persistence in this step.

## Verification

Commands run in `product/frontend`:

```text
npm run lint
npm run build
```

Result:

- TypeScript check passed.
- Vite production build passed.
- Existing chunk-size warning only.

## Notes

`MeihuaAnalysis.vue` is intentionally a local frontend prototype. It supports number/text/time casting and displays 本卦、互卦、变卦、动爻、体用生克 and a short action suggestion. Formal business integration should later add runtime config, pricing, backend calculation, review records, history, points ledger, and LLM rendering boundaries.
