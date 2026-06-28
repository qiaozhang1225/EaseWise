# EaseWise AI Studio Export 8 Follow-Up Bundle - Birth Date And Birth Location Pickers

## Objective

Refine only the Four Pillars `出生生辰` and `出生地区` pickers in AI Studio. Export 8 is broadly acceptable, and several parts look better than the current local frontend. This round should preserve those gains and narrow the next iteration to picker correctness and data-structure readiness.

## Current AI Studio Export

- Zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (8).zip`
- SHA256: `3487a803780ea6935cdc87152eb9673e1dc59f807fe3bb1234a971b6dbcd93ef`
- Changed files:

```text
src/components/analysis/Analysis.vue
src/components/four-pillars/FourPillarsAnalysis.vue
src/components/four-pillars/FourPillarsNatalTable.vue
src/types/api.ts
```

## Preserve From Export 8

Do not regress the following:

- 袁天罡称骨 visual treatment.
- Manual numeric fields plus wheel-input combination.
- Bottom sheet direction and mobile feel.
- 土 / 金 color distinction.
- Element-colored 大运 / 流年 selector text without outer circles.
- 命盘 and 流年 row typography refinements.

## Narrow Scope For Next AI Studio Iteration

Only focus on:

1. `出生生辰` picker.
2. `出生地区` picker.

Recommended target files:

```text
src/components/four-pillars/FourPillarsAnalysis.vue
server.ts
src/types/api.ts only if needed
```

## Birth Date Picker Requirements

### User Intent

When tapping `出生生辰`, the bottom sheet should present clear calendar-mode choices. `公历` and `农历` are not just labels; they should select different input modes.

### Required Structure

The top row of the bottom sheet should contain:

- Segmented tabs: `公历 / 农历`
- Confirm button on the right.

The selected tab must sync with the main form calendar mode.

### Solar Mode

Solar mode should show:

- Manual numeric fields: 年 / 月 / 日 / 时 / 分.
- Wheel columns: 年 / 月 / 日 / 时 / 分.
- Month/day display uses Gregorian numeric values, e.g. `05`, `22`.
- Hour wheel can show the traditional hour branch as a small secondary label.

### Lunar Mode

Lunar mode should show:

- Manual numeric fields: 年 / 月 / 日 / 时 / 分.
- Wheel columns: 年 / 月 / 日 / 时 / 分.
- Month/day wheel labels should use lunar labels where helpful, e.g. `四`, `十八`, while manual fields may remain numeric.
- No visible leap-month control in this cycle.
- Confirm should resolve lunar input through mock/local resolver behavior and then update the main summary.

### Manual Fields

Keep the export 8 idea of manual fields above wheels. Use clamped input:

```text
year: 1801-2099
month: 1-12
day: 1-31
hour: 0-23
minute: 0-59
```

Do not use native browser date/time pickers.

### Wheel Behavior

Scrolling a wheel should commit the centered value automatically. Confirm should not require an extra tap after scrolling.

## Birth Location Picker Requirements

### User Intent

The current export 8 location picker has a pleasant bottom-sheet direction but its mock data is too flat. It cannot prove whether the design handles realistic Chinese province/city/district data.

### Real Local Data Shape

Local frontend expects:

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

Example local records:

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

```json
{
  "id": "cn-110105",
  "scope": "domestic",
  "country": "中国",
  "province": "北京市",
  "city": "北京市",
  "district": "朝阳区",
  "region": "",
  "display_name": "中国 北京市 北京市 朝阳区",
  "latitude": 39.921489,
  "longitude": 116.486409,
  "timezone": "Asia/Shanghai"
}
```

### Mock Data Minimum

AI Studio does not need to paste the complete 5377-record local dataset, but `server.ts` or the component mock must include a realistic structured subset:

- At least 8-10 domestic provinces or municipalities.
- At least 2-3 cities for normal provinces.
- At least 4-8 districts for Beijing/Shanghai/Guangzhou/Shenzhen or similar key cities.
- At least 8-12 overseas countries.
- At least 2-4 cities/regions for large overseas countries.
- Every item must include `id`, `scope`, `display_name`, `latitude`, `longitude`, `timezone`, and the matching hierarchy fields.

### Picker UI

Domestic mode:

```text
国内 tab
省份 wheel | 城市 wheel | 区县 wheel
```

Overseas mode:

```text
海外 tab
国家 wheel | 地区/城市 wheel
```

Also keep:

- Search field.
- Search results as list cards using `display_name`, coordinates, and timezone.
- Confirm button in the same visual row as the mode tabs.
- Compact sheet height matching the date picker.
- Bottom nav safe offset.

### State Rules

When province changes:

- City resets to the first city in that province.
- District resets to the first district in that city.

When city changes:

- District resets to the first district in that city.

When selecting a search result:

- It should update the selected location id.
- It should switch domestic/overseas mode based on the record scope.
- It should update the main summary and true solar preview.

## Mock API Shape

If adding or adjusting a mock endpoint in AI Studio `server.ts`, use:

```text
GET /api/v1/four-pillars/input/locations
```

Response shape:

```json
{
  "default_location_id": "cn-110101",
  "locations": []
}
```

The local frontend already calls `listFourPillarsBirthLocations()` and normalizes this shape.

## Do Not Change

- Do not change the natal chart result page.
- Do not change Yuan Tiangang bone-weight layout.
- Do not change luck-cycle table and selector styling.
- Do not change phone QiMen page.
- Do not change auth, points, payment, unlock, route, or API contracts except mock data needed for this picker.
- Do not reintroduce a visible `四柱` input mode in this picker round.
- Do not use flat city-only `locationOptions` as the primary data model.

## Acceptance Checklist

- Date bottom sheet has visible `公历 / 农历` tabs.
- Main form calendar mode and bottom-sheet selected tab stay in sync.
- Solar mode uses Gregorian numeric wheel labels.
- Lunar mode uses lunar month/day labels in the wheel while keeping manual numeric fields.
- Manual fields and wheels remain visually integrated.
- Wheel scroll auto-commits centered values.
- Location bottom sheet has `国内 / 海外` tabs.
- Domestic location picker uses three wheels: province, city, district.
- Overseas location picker uses two wheels: country, region/city.
- Mock location data is structured and large enough to test real hierarchy, not a flat city list.
- Search works across `display_name`.
- Confirm updates the main page summary and true solar time preview.
- No unrelated pages/components are modified.
