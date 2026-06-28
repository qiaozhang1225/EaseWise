# Four Pillars Input Design Merge From AI Studio Export 9

## Scope

Only the Four Pillars input-page birth datetime and birth location interaction design was merged into the local frontend. Local API, true-solar-time preview, structured location data, auth, points deduction, review creation, polling, result rendering, and luck-cycle logic were preserved.

## Imported Design Ideas

- Birth date and birth location rows now use a more explicit picker-row layout with icon, label, value, chevron, and pressed feedback.
- Birth location row adds a restrained breathing marker animation to make the location calibration affordance visible without changing behavior.
- Bottom sheets now more closely match the AI Studio export: bottom-up overlay, blurred dark backdrop, rounded top sheet, handle bar, title/subtitle, and confirm button aligned with the segmented control.
- Date picker keeps the local `公历 / 农历` split and adds a richer manual numeric area with visible units.
- Date wheels keep local scroll-snap auto-selection behavior, but use a stronger center highlight, larger selected typography, fade masks, and hour secondary labels such as `辰时`.
- Location picker keeps the local structured domestic/overseas real data and endpoint-backed selection, while adding the same sheet visual system and a selected-location preview card.
- Follow-up pixel pass removed AI Studio's black/gold and gold-accent treatment. The picker now keeps the AI Studio geometry, bottom-sheet rhythm, wheel proportions, and manual-input composition, but maps accents to the local EaseWise indigo/blue-gray design language.
- The bottom sheet now reserves `96px` for the local bottom navigation after mobile visual verification, so it opens from just above the nav rather than being partially covered.

## Preserved Boundaries

- Did not import AI Studio `mockLocations.ts`.
- Did not re-enable the removed `四柱` manual ganzhi input mode in the UI.
- Did not modify backend payloads or endpoints.
- Did not change natal-chart result, luck-cycle table, Meihua, homepage, pricing, or points behavior in this slice.

## Verification

- `npm run lint`
- `npm run build`
- Headless Chrome mobile viewport check at `390x844`: date drawer clears the bottom navigation by about `2.5px`; gold-style computed-color matches were `0`.

Both checks passed. Vite still reports the existing large chunk warning after minification; it is not caused by this merge.
