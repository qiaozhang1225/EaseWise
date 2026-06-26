# Export 7 Verification

## Static Checks
- `npm run build` in `product/frontend`: passed.
- `npm run lint` in `product/frontend`: passed.

## Build Notes
- Vite build completed successfully.
- Existing Rollup chunk-size warning remains informational and unrelated to this merge.

## Manual Review Targets
- Four Pillars natal result table:
  - Rows below `藏干` appear as `地势`, `自坐`, `旬空`, `纳音`, `神煞`.
  - `神煞` collapsed state shows at most two names plus `+N 更多` per overflowing pillar.
  - Arrow-only toggle expands/collapses the whole shen-sha row.

- Four Pillars luck table:
  - Shen-sha cells use plain text styling consistent with the natal table.
  - Overflow behavior mirrors the natal table.
  - Existing luck-cycle/year generation controls remain intact.
