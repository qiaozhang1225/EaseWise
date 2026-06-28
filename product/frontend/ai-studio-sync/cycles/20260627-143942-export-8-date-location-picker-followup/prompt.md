# AI Studio Sync Request

## Objective

Please refine only the Four Pillars `出生生辰` and `出生地区` pickers from export 8. Export 8 is mostly in a good direction; preserve its stronger styling and do not touch unrelated areas.

## Source Hierarchy

- Local repo behavior is authoritative for real routes, APIs, auth, validation, state, persistence, payments, and business behavior.
- Local data shape is authoritative for birth-location records and input payloads.
- Latest AI Studio zip is authoritative only for AI Studio's current design output.
- This Markdown bundle is the handoff contract for the next AI Studio iteration.

## Local Frontend Changes

The local app now has structured Four Pillars input support:

- `出生生辰` supports separate `公历 / 农历` modes.
- Manual numeric fields and wheel pickers should work together.
- `出生地区` is based on structured records with country/province/city/district, coordinates, timezone, and display name.
- The real location endpoint shape is:

```text
GET /api/v1/four-pillars/input/locations
```

```json
{
  "default_location_id": "cn-110101",
  "locations": []
}
```

Local location item shape:

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

Example:

```json
{
  "id": "cn-110101",
  "scope": "domestic",
  "country": "中国",
  "province": "北京市",
  "city": "北京市",
  "district": "东城区",
  "region": "",
  "display_name": "中国 北京市 北京市 东城区",
  "latitude": 39.917544,
  "longitude": 116.418757,
  "timezone": "Asia/Shanghai"
}
```

## Current AI Studio Export

Export 8 zip SHA256:

```text
3487a803780ea6935cdc87152eb9673e1dc59f807fe3bb1234a971b6dbcd93ef
```

Export 8 changed:

```text
src/components/analysis/Analysis.vue
src/components/four-pillars/FourPillarsAnalysis.vue
src/components/four-pillars/FourPillarsNatalTable.vue
src/types/api.ts
```

Please preserve the good parts from export 8:

- 袁天罡称骨 display.
- Manual numeric fields plus wheel picker visual combination.
- Bottom sheet direction and mobile feel.
- 土/金 color distinction.
- Element-colored 大运/流年 selector text.
- 命盘 and 流年 row typography refinements.

## Gap To Close

Only two gaps should be closed now:

1. `出生生辰`: the picker needs clearly separated `公历 / 农历` choices, with different content and synchronized state.
2. `出生地区`: the picker must adapt to realistic structured data, not a flat city list with too few mock records.

## Design Task

### Birth Date Picker

Update `src/components/four-pillars/FourPillarsAnalysis.vue`.

When tapping `出生生辰`, show a bottom sheet with:

- Top row: segmented tabs `公历 / 农历` on the left, confirm button on the right.
- Bottom-sheet tab and main form calendar mode must stay synchronized.
- Bottom sheet must remain bottom-navigation-safe.

Solar tab:

- Manual fields: 年 / 月 / 日 / 时 / 分.
- Wheels: 年 / 月 / 日 / 时 / 分.
- Month/day use Gregorian numeric display such as `05`, `22`.

Lunar tab:

- Manual fields: 年 / 月 / 日 / 时 / 分.
- Wheels: 年 / 月 / 日 / 时 / 分.
- Month/day wheel labels may use lunar labels, such as `四`, `十八`.
- Manual fields remain numeric.
- Do not show a leap-month control in this round.

Manual input ranges:

```text
year: 1801-2099
month: 1-12
day: 1-31
hour: 0-23
minute: 0-59
```

Do not use native browser date or time pickers.

Wheel scrolling must commit the centered selected value automatically; users should not need to tap again after scrolling.

### Birth Location Picker

Update `src/components/four-pillars/FourPillarsAnalysis.vue` and AI Studio `server.ts` mock data if needed.

Replace the flat city-list mental model with structured records:

Domestic:

```text
国内 tab
省份 wheel | 城市 wheel | 区县 wheel
```

Overseas:

```text
海外 tab
国家 wheel | 地区/城市 wheel
```

Keep:

- Search input.
- Search result cards.
- Coordinates and timezone display.
- Confirm button in the same visual row as the tabs.
- Compact height similar to the date picker.
- Bottom-nav-safe offset.

State behavior:

- Changing province resets city and district to valid first options.
- Changing city resets district to a valid first option.
- Selecting search result updates selected id, scope, main summary, and true solar preview.

## Mock Data And States

Please add enough structured mock data for visual testing. Do not keep only a few flat city items.

Minimum mock data:

- 8-10 domestic provinces/municipalities.
- 2-3 cities per normal province.
- 4-8 districts for major cities like 北京、上海、广州、深圳.
- 8-12 overseas countries.
- 2-4 cities/regions for large overseas countries.

Every location item should include:

```text
id, scope, display_name, latitude, longitude, timezone,
country, province/city/district for domestic,
country/region/city for overseas
```

Mock endpoint:

```text
GET /api/v1/four-pillars/input/locations
```

Response:

```json
{
  "default_location_id": "cn-110101",
  "locations": [
    {
      "id": "cn-110101",
      "scope": "domestic",
      "country": "中国",
      "province": "北京市",
      "city": "北京市",
      "district": "东城区",
      "display_name": "中国 北京市 北京市 东城区",
      "latitude": 39.917544,
      "longitude": 116.418757,
      "timezone": "Asia/Shanghai"
    }
  ]
}
```

## Do Not Change

- Do not change `FourPillarsNatalTable.vue` unless a type import is absolutely necessary.
- Do not change Yuan Tiangang bone-weight display.
- Do not change luck-cycle selector or table styling.
- Do not change phone QiMen page.
- Do not change profile, AI agent, recharge, auth, points, payment, unlock, route, or persistence behavior.
- Do not reintroduce a visible `四柱` input mode.
- Do not use flat city-only `locationOptions` as the primary model.
- Do not use native browser date/time controls.

## Acceptance Checklist

- Changed files are limited mainly to `src/components/four-pillars/FourPillarsAnalysis.vue`, `server.ts`, and optionally `src/types/api.ts`.
- Date picker opens from bottom and is not covered by bottom nav.
- Date picker visibly has `公历 / 农历` tabs.
- Main form calendar mode and date picker tab stay synchronized.
- Solar mode has Gregorian numeric wheel labels.
- Lunar mode has lunar month/day wheel labels, while manual fields remain numeric.
- Manual fields and wheels remain visually integrated.
- Scrolling a wheel commits the centered value automatically.
- Location picker opens from bottom and is not covered by bottom nav.
- Domestic mode uses province/city/district wheels.
- Overseas mode uses country/region wheels.
- Search works over `display_name`.
- Mock locations are structured and sufficiently rich to test hierarchy.
- Choosing a location updates summary and true solar preview.
- No unrelated page or result-view styling is changed.
