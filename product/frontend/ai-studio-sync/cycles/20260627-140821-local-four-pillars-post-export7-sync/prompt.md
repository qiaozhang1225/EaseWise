# Prompt For AI Studio

You are updating the EaseWise Vue 3 + Vite H5 prototype. The current AI Studio export 7 is behind the local repository. Please sync the prototype to match the local frontend behavior and visual state described below.

## Source Of Truth

The local EaseWise repo is authoritative for architecture, routes, APIs, auth, points, pricing, unlock behavior, and state management. AI Studio is only responsible for mirroring the current local frontend design and using mock backend data that is rich enough to demonstrate it.

Keep the Vue 3 + Vite architecture. Do not convert to React, TSX, or a different app structure.

## Baseline

Previous AI Studio export cycle:

```text
20260625-170000-export-7-four-pillars-shensha-merge
```

Previous AI Studio zip SHA256:

```text
4059a24cc34a20e6e5e356701529d78ce5be05671ae477902487e606d2b8fd7c
```

Local code has moved ahead after that export. Please update the AI Studio prototype to match the new local behavior.

## Files To Focus On

Main frontend files:

```text
src/components/analysis/Analysis.vue
src/components/four-pillars/FourPillarsAnalysis.vue
src/components/four-pillars/FourPillarsNatalTable.vue
src/types/api.ts
src/lib/api.ts
server.ts
```

Use `server.ts` only for AI Studio mock compatibility. Do not use it as business truth.

## Required Updates

### 1. Phone QiMen and Four Pillars Entry Cards

Make the phone QiMen input page and Four Pillars input page use a consistent compact title card.

Design:

- White rounded card.
- Small translucent circular mark at top right.
- Animated dot before title using `animate-ping`.
- Title uses `font-serif text-[16px] font-black text-brand-gold-fixed`.
- No explanatory paragraph below the title.

Phone title:

```text
奇门遁甲手机号综合测评
```

Four Pillars title:

```text
四柱八字综合测评
```

Both submit buttons must use the same icon and wording pattern:

```text
立即扣除 XX 积分，深度智能测算
```

Keep the `Sparkles` icon in both buttons. In Four Pillars, place the button outside the form card so it visually matches the phone page.

### 2. Four Pillars Input Page Layout

Make the Four Pillars input page compact:

- Title card first.
- White form card below.
- Name input first.
- Second row: gender segmented control on the left, calendar mode segmented control on the right.
- Calendar mode only shows `公历 / 农历`. Do not show a visible `四柱` mode in the main input page.
- Birth date and birth location are read-only summary rows that open bottom sheets.
- Birth location summary should show true solar time preview.

### 3. Date Picker Bottom Sheet

The date picker must open from the bottom, not from the left.

It must sit above the bottom navigation and must not be covered by the bottom nav.

Use a bottom-sheet style:

- Dark translucent overlay.
- Sheet aligned to bottom.
- Rounded top corners.
- Compact height.
- Same general height rhythm as the location picker.

### 4. Manual Numeric Inputs Above Wheels

Add pure manual numeric hand-fill fields above the wheel selector.

Important: do not use native browser date or time pickers. The user specifically wants separate numeric fields.

For solar tab, show five inputs:

```text
年 / 月 / 日 / 时 / 分
```

For lunar tab, show five inputs:

```text
年 / 月 / 日 / 时 / 分
```

Each input should be aligned above the corresponding wheel column.

Use clamped numeric ranges:

```text
year: 1801-2099
month: 1-12
day: 1-31
hour: 0-23
minute: 0-59
```

When the user edits a field, update the selected wheel value and date state immediately.

Code-level behavior to include:

```ts
function clampNumber(value: string | number, min: number, max: number, fallback: number): number {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return fallback;
  return Math.min(max, Math.max(min, Math.trunc(numericValue)));
}
```

Then implement `handleSolarManualInput()` and `handleLunarManualInput()` to call `setSolarPart()` and `setLunarPart()`.

### 5. Wheel Scroll Must Commit Automatically

The current local fix detects which wheel option is centered after scrolling. Please implement the same behavior.

Before confirming the date drawer, sync the centered wheel values into state.

This prevents the bug where the wheel visually changes but the value is not actually selected until a tap.

Solar confirm behavior:

- Sync centered wheel selection.
- Close drawer immediately.
- Refresh true solar preview in the background.

### 6. Location Picker and Mock Location Data

The location picker style is acceptable only if it is compact and bottom-sheet based. It must not have excessive blank vertical space.

The data must be usable:

- Domestic should include multiple provinces.
- Each province should include multiple cities.
- Each city should include multiple districts.
- Overseas should include common countries and major cities/regions.
- Default location is Beijing.

Do not leave the mock dataset at only `北京市东城区`.

For AI Studio, the full local `birth-locations.json` does not need to be copied if it is too large, but the mock must be large enough to test the UI realistically.

### 7. True Solar Time

Do not display `未校准` when default Beijing is available.

Default behavior:

- Use Beijing if the user has not selected a birth location.
- Show a computed or mock true solar time string.
- In the result modal, fallback text can be `按默认北京真太阳时校准` only if no exact time is available.

### 8. Waiting Animation and Result Readiness

The local app fixed two stuck states:

- Stuck at stage 1.
- Stuck at stage 4.

Update the AI Studio prototype so Four Pillars generation:

- Enters waiting state immediately after submit.
- Runs the waiting animation while submit and polling are pending.
- Does not wait forever for long-form LLM text.
- Shows the result once a renderable chart is present.

Renderable chart rule:

```text
If review.chart_display.pillars has four keys, or review.chart.pillars has four keys, the result page can render.
```

Use an equivalent helper to `hasRenderableFourPillarsResult()`.

### 9. Natal Chart Header

Update `FourPillarsNatalTable.vue`.

The chart header should be compact:

- Left block: user icon plus two stacked lines, e.g. `男命` and `乾造`.
- Date block: calendar icon plus two stacked lines.
- First date line: `公历 YYYY-MM-DD HH:mm`.
- Second date line: `农历 YYYY-MM-DD 辰时`.
- Do not use `1989年4月18日` in the compact header. Use `1989-04-18`.
- Keep a space between date and hour branch, e.g. `1989-04-18 辰时`.
- Button text must be `更多命盘信息`.

### 10. More Chart Info Modal

The more-info view should be a centered modal, not a bottom sheet.

Design:

- Centered overlay.
- Width about 360px on mobile.
- Max height about 80vh.
- Internal scroll.
- Header text: `更多命盘信息`.

Do not split `基本信息` and `专业参数` into separate sections. Merge them into one info grid.

Include these fields:

```text
姓名
性别
公历
农历
生肖
出生地区
出生节气
星座
星宿
真太阳时
胎元
空亡
命宫
胎息
身宫
命卦
```

Five-element energy:

- Restore progress bars for 木/火/土/金/水.
- `旺衰初判` should occupy a full row.
- `喜用候选` on the lower left.
- `忌神候选` on the lower right.

### 11. Yuan Tiangang Bone Weight

Add complete mock data and UI display for Yuan Tiangang bone weight.

Required fields:

```ts
bone_weight: {
  total_qian: number;
  total_label: string;
  summary: string;
  fate_pattern?: string | null;
  verse?: string | null;
  year_ganzhi: string;
  lunar_month: number;
  lunar_day: number;
  hour_branch: string;
  parts: Record<string, number>;
  rules: Record<string, string>;
  sources: Array<{ title: string; url: string }>;
}
```

For the common test case `1989-05-22 08:55`, show four-liang-one-qian and this verse:

```text
此命推来事不同，为人能干亦凡庸，中年还有逍遥福，不比前时运未通
```

Display the verse as two lines:

```text
此命推来事不同，为人能干亦凡庸
中年还有逍遥福，不比前时运未通
```

Also display:

- Total weight.
- Year/month/day/hour bone parts.
- 格局 or summary.
- A note that bone weight is traditional reference content and does not participate in the main score.

### 12. Mock Server Requirements

Update `server.ts` mock responses so the frontend can render everything.

`chart_display.profile` must include enough fields:

```text
name, gender_label, structure_label, zodiac,
solar_datetime_text, lunar_date, lunar_full_text,
birth_place, timezone, solar_term_context,
input_mode, standard_birth_datetime, effective_birth_datetime,
true_solar_time, birth_location, true_solar_time_text,
constellation, xiu, tai_yuan, tai_xi, ming_gong, shen_gong,
life_gua, empty_branches_text, pillar_xun_kong_text,
bone_weight
```

Mock chart data must include:

- Four pillars.
- Element counts.
- Strength label.
- Favorable elements.
- Unfavorable elements.
- Luck cycles and annual years rich enough to test horizontal scrolling.
- Shen-sha and xun-kong rows where the UI expects them.

### 13. Do Not Change

- Do not remove or redesign phone QiMen.
- Do not remove login or registered-user gating.
- Do not change points costs except through existing runtime config.
- Do not remove insufficient-points 402 behavior.
- Do not introduce a visible `四柱` input mode on the main input page.
- Do not use native browser date/time controls.
- Do not show empty location datasets.
- Do not show `未校准` for true solar time when Beijing default exists.
- Do not wait for all LLM text before displaying the natal chart result.

## Acceptance Checklist

Please verify before returning the updated code:

- Vue 3 + Vite app still builds.
- Phone and Four Pillars title cards match.
- Both CTAs include Sparkles and `深度智能测算`.
- Four Pillars form is compact.
- Date picker opens from bottom and sits above bottom nav.
- Date picker has manual numeric fields plus wheels.
- Wheel scroll auto-selects centered value.
- Solar confirm closes immediately.
- Lunar confirm resolves date and closes without doing nothing.
- Location picker has enough domestic and overseas data.
- True solar time displays without `未校准`.
- Waiting flow does not stick at phase 1 or phase 4.
- Result renders as soon as four chart pillars exist.
- Header button says `更多命盘信息`.
- Modal contains merged info grid, five-element bars, true solar time, and bone weight.
- Bone-weight verse is visible and split into two lines.

Return a concise summary of changed files and any mock-data assumptions.
