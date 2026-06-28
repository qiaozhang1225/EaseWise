# AI Studio Export 8 Picker Audit

## Source

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (8).zip`
- SHA256: `3487a803780ea6935cdc87152eb9673e1dc59f807fe3bb1234a971b6dbcd93ef`
- Registered local cache cycle: `.aistudio-sync/cycles/20260627-063909-export-8-date-location-picker-focus`

## Export 8 Changed Files

AI Studio export 8 changed:

```text
src/components/analysis/Analysis.vue
src/components/four-pillars/FourPillarsAnalysis.vue
src/components/four-pillars/FourPillarsNatalTable.vue
src/types/api.ts
```

## What Improved

The export made several useful design moves that should be preserved:

- The manual numeric date fields plus wheel picker feel better than the current local-only version.
- The date picker bottom sheet is directionally correct and mobile-friendly.
- The Yuan Tiangang bone-weight section is visually stronger.
- Five-element colors are more legible; 土 and 金 are clearly separated.
- Luck-cycle selector typography and element-colored text are cleaner.

## Picker Gaps Still Open

This follow-up should only target the two picker areas below.

### Birth Date Picker

Current AI Studio export 8 has a good manual-field + wheel combination, but the calendar modes are not fully separated:

- The user expects visible mode choices for `公历` and `农历` when opening the birth-date picker.
- The two modes should have different picker content.
- Solar mode should use Gregorian numeric month/day display.
- Lunar mode should use lunar month/day text display where appropriate, while still allowing manual numeric input.
- The main form's calendar mode and the bottom sheet tabs must stay synchronized.

### Birth Location Picker

Export 8 currently uses a flat `locationOptions` list:

```ts
const locationOptions = [
  { name: '北京', province: '直辖市', timezone: 'UTC+8', longitude: 116.4, latitude: 39.9 },
  ...
]
```

That is not compatible with the real local data shape or the desired picker structure.

The local app expects structured location records:

```ts
type BirthLocationOption = {
  id: string;
  scope: string;
  display_name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  country?: string;
  province?: string;
  city?: string;
  district?: string;
  region?: string;
};
```

The local API endpoint is:

```ts
GET /api/v1/four-pillars/input/locations
```

Frontend client:

```ts
export function listFourPillarsBirthLocations(): Promise<Record<string, unknown>> {
  return requestJson<Record<string, unknown>>('/api/v1/four-pillars/input/locations');
}
```

The local structured data contains 5377 location records. AI Studio does not need the full dataset, but its mock data must use the same structure and must be large enough to test:

- Domestic: province -> city -> district wheels.
- Overseas: country -> region/city wheels.
- Search over `display_name`.
- Default location id.
- Coordinates and timezone display.

## Recommended Next Slice

Only update:

```text
src/components/four-pillars/FourPillarsAnalysis.vue
server.ts
src/types/api.ts if needed
```

Do not modify:

```text
src/components/four-pillars/FourPillarsNatalTable.vue
Luck cycle styling
Yuan Tiangang bone-weight layout
Five-element palette
Phone QiMen page
Profile page
AI agent page
```

This round is a picker refinement only.
