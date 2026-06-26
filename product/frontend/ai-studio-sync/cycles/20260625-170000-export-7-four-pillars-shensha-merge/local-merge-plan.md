# Export 7 Local Merge Plan

## Source
- AI Studio zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (7).zip`
- SHA256: `4059a24cc34a20e6e5e356701529d78ce5be05671ae477902487e606d2b8fd7c`
- Registered cycle: `20260625-170000-export-7-four-pillars-shensha-merge`

## Imported Into Local Frontend
- `product/frontend/src/components/four-pillars/FourPillarsNatalTable.vue`
  - Reordered lower natal rows after hidden stems to `地势`, `自坐`, `旬空`, `纳音`, `神煞`.
  - Kept shen-sha sorting with favorable items first, neutral middle, caution/risk last.
  - Changed collapsed overflow to show at most two items plus `+N 更多`.
  - Replaced colored badge rendering with plain text that matches the natal table's detail rows.
  - Kept an arrow-only expand/collapse control below the `神煞` row label.

- `product/frontend/src/components/four-pillars/FourPillarsAnalysis.vue`
  - Applied the same shen-sha sorting and collapsed overflow behavior to the luck table.
  - Changed luck-table shen-sha rendering from colored badges to plain text.
  - Aligned luck-table text sizing and family with the natal table detail rows.
  - Kept the previously merged four-stage generation waiting flow and local API state machine.

## Not Imported
- AI Studio `server.ts` mock-data changes remain archive evidence only.
- No local backend API, point deduction, auth, polling, or payment logic was changed.
- No unrelated AI Studio component edits were merged.
