# Local Merge Verification

## Applied

- Rebuilt the Four Pillars input page to match AI Studio export 10 structure:
  - centered header title/subtitle plus refresh affordance
  - compact title card with points badge
  - white form card
  - name input
  - side-by-side gender and calendar segmented controls
  - birth datetime read-only summary row
  - birth location read-only summary row
  - card-contained CTA
- Replaced the previous local picker-row implementation with export 10 style bottom sheets:
  - top handle
  - segmented tab group plus confirm button
  - manual numeric date input strip
  - five-column snap wheel picker
  - structured domestic/overseas location picker with search and current selection panel

## Preserved

- Local app state, API calls, auth, points, review generation, polling, true-solar preview, lunar conversion, and location endpoint data.
- The local indigo/blue-gray visual language. Gold/black-gold accents from prior experiments were not used.

## Checks

- `npm run lint`: passed.
- `npm run build`: passed.
- Mobile viewport `390x844` via headless Chrome:
  - date drawer opens from bottom and includes `手动数字输入`, `公历`, `农历`.
  - location drawer includes `国内地区`, `海外地区`, `当前选择`.
  - drawer clears bottom navigation by about `2.5px`.
  - gold-style computed-color matches: `0`.

## Notes

- Vite still reports the existing large chunk warning after minification.
