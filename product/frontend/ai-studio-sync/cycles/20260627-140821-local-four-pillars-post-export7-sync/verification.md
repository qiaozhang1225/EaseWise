# Verification Notes

## Local Checks

The latest local frontend change, which added manual numeric date fields above the wheels, was checked with:

```text
npm run lint
npm run build
```

Result:

- TypeScript check passed.
- Vite build passed.
- Existing chunk-size warning only.

## Sync Package Checks

This cycle intentionally contains Markdown instructions only. It does not copy the full 83,988-line birth-location dataset into AI Studio. The prompt instructs AI Studio to either keep a practical mock subset or generate a richer mock enough for UI validation.

## Manual QA Scenarios For AI Studio

1. Open Four Pillars input page.
2. Confirm title card matches phone QiMen title-card style.
3. Open birth-date picker.
4. Confirm it opens from bottom, above bottom nav.
5. In solar mode, type into manual year/month/day/hour/minute fields and verify wheel/state sync.
6. Scroll wheels without tapping and press confirm. The centered values should be used.
7. Switch to lunar mode and repeat.
8. Open birth-location picker and confirm domestic/overseas data is not a single Beijing-only item.
9. Submit a Four Pillars review.
10. Waiting flow should not stay stuck at phase 1 or phase 4.
11. Result page should render once four pillars are available.
12. Open `更多命盘信息`.
13. Confirm true solar time is visible, not `未校准`.
14. Confirm five-element bars are visible.
15. Confirm Yuan Tiangang bone-weight result includes total, parts, fate pattern, and two-line verse.
