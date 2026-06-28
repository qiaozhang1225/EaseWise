# EaseWise Local Reverse Sync Bundle - Post Export 7 Four Pillars Input and Chart Polish

## Purpose

This bundle is for syncing local EaseWise frontend/backend progress back into AI Studio. AI Studio export 7 is no longer current. The local repo now contains a more complete Four Pillars input flow, true solar time support, complete birth-location data, a richer natal chart info modal, a stabilized waiting flow, and unified entry-page visual language.

AI Studio should update its Vue 3 + Vite prototype to match these local changes visually and structurally, while keeping the prototype nature of AI Studio's `server.ts` mock backend.

## Source Hierarchy

1. Local EaseWise repo is the source of truth for architecture, routes, APIs, auth, pricing, state, and business behavior.
2. AI Studio should only mirror local UI/UX and mock enough data to demonstrate the local frontend state.
3. Do not replace Vue 3 + Vite with React, TSX, or a new app structure.
4. Do not invent new pricing, login, points, payment, unlock, or routing behavior.

## Baseline

- Previous AI Studio cycle: `20260625-170000-export-7-four-pillars-shensha-merge`
- Previous AI Studio zip SHA256: `4059a24cc34a20e6e5e356701529d78ce5be05671ae477902487e606d2b8fd7c`
- Local baseline after export 7 archive: `eac3f4e`
- Current local HEAD: `897d3c1`
- Current uncommitted local addition: manual numeric date fields in `FourPillarsAnalysis.vue`

## High-Level Changes To Mirror

### 1. Unified Function Entry Cards

Files:

- `product/frontend/src/components/analysis/Analysis.vue`
- `product/frontend/src/components/four-pillars/FourPillarsAnalysis.vue`

Phone QiMen and Four Pillars input pages should share the same compact title-card language:

- White rounded card.
- Translucent circle mark in the top-right corner.
- Small animated primary-color dot before title.
- 16px serif gold title.
- No long explanatory paragraph under the title.

Phone title:

```vue
<section class="bg-white rounded-2xl p-4.5 border border-gray-100 shadow-sm relative overflow-hidden text-left font-sans">
  <div class="absolute -right-3 -top-3 w-16 h-16 bg-brand-primary/5 rounded-full"></div>
  <div class="relative flex items-center gap-2">
    <span class="relative flex h-2.5 w-2.5 shrink-0">
      <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-primary/50"></span>
      <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-brand-primary"></span>
    </span>
    <h2 class="font-serif text-[16px] font-black text-brand-gold-fixed leading-snug">奇门遁甲手机号综合测评</h2>
  </div>
</section>
```

Four Pillars title should use the same structure with:

```text
四柱八字综合测评
```

Both submit buttons should have the same icon and text pattern:

```vue
<Sparkles :size="15" fill="currentColor" />
<span>立即扣除 <span class="font-sans">{{ points }}</span> 积分，深度智能测算</span>
```

The Four Pillars submit button belongs outside the form card, matching the phone page button rhythm.

### 2. Four Pillars Compact Input Page

File:

- `product/frontend/src/components/four-pillars/FourPillarsAnalysis.vue`

The current local input page has:

- A clean title card at the top.
- A compact white input card.
- Name input as the first row.
- Gender segmented control on the left.
- Calendar mode segmented control on the right.
- Only `公历 / 农历` modes in the main visible selector. The previous `四柱` visible input mode is removed.
- Birth date summary button.
- Birth location summary button with true solar time preview.
- Submit CTA outside the card.

Important layout anchor:

```vue
<div class="grid grid-cols-[112px_1fr] gap-2 items-center">
  <div class="grid grid-cols-2 rounded-xl bg-brand-paper p-1">
    <button class="h-8 rounded-lg text-[12px] font-bold" :class="gender === 'male' ? 'bg-brand-primary text-white' : 'text-brand-secondary'">男</button>
    <button class="h-8 rounded-lg text-[12px] font-bold" :class="gender === 'female' ? 'bg-brand-primary text-white' : 'text-brand-secondary'">女</button>
  </div>
  <div class="grid grid-cols-2 rounded-xl bg-brand-paper p-1 w-[148px] justify-self-end">
    <button v-for="mode in ['solar', 'lunar']" :key="mode" class="h-8 rounded-lg text-[11px] font-bold">
      {{ mode === 'solar' ? '公历' : '农历' }}
    </button>
  </div>
</div>
```

### 3. Date Bottom Sheet Must Come From Bottom

The date and location picker must be a bottom sheet, not a left drawer.

Behavior requirements:

- Opens from bottom.
- Sits above the bottom navigation.
- Does not get covered by `BottomNav`.
- Has dark translucent overlay.
- Uses a rounded top sheet.
- Height is compact and comparable between date picker and location picker.

AI Studio should not render this as a side panel.

### 4. Solar/Lunar Date Picker With Manual Numeric Fields

The latest local UI adds pure manual numeric inputs above the wheel selector. This was added because the user explicitly did not want native date/time fields.

Required behavior:

- In solar tab: show five numeric inputs for 年/月/日/时/分.
- In lunar tab: show five numeric inputs for 年/月/日/时/分.
- Inputs are above the wheel label row.
- Inputs are compact and aligned with the wheel columns.
- Editing an input immediately updates the local selected value.
- Values are clamped.
- Wheel scroll still works.
- Confirm calls a final wheel-center sync before closing.

Script anchors:

```ts
function clampNumber(value: string | number, min: number, max: number, fallback: number): number {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return fallback;
  return Math.min(max, Math.max(min, Math.trunc(numericValue)));
}

function handleSolarManualInput(part: 'year' | 'month' | 'day' | 'hour' | 'minute', event: Event): void {
  const rawValue = String((event.target as HTMLInputElement | null)?.value || '');
  const fallbackMap = {
    year: Number(birthYear.value || 1989),
    month: Number(birthMonth.value || 1),
    day: Number(birthDay.value || 1),
    hour: solarHour.value,
    minute: solarMinute.value,
  };
  const ranges: Record<typeof part, [number, number]> = {
    year: [1801, 2099],
    month: [1, 12],
    day: [1, 31],
    hour: [0, 23],
    minute: [0, 59],
  };
  const [min, max] = ranges[part];
  const nextValue = clampNumber(rawValue, min, max, fallbackMap[part]);
  setSolarPart(part, nextValue);
}

function handleLunarManualInput(part: 'year' | 'month' | 'day' | 'hour' | 'minute', event: Event): void {
  const rawValue = String((event.target as HTMLInputElement | null)?.value || '');
  const fallback = Number(lunarInput.value[part]) || 0;
  const ranges: Record<typeof part, [number, number]> = {
    year: [1801, 2099],
    month: [1, 12],
    day: [1, 31],
    hour: [0, 23],
    minute: [0, 59],
  };
  const [min, max] = ranges[part];
  setLunarPart(part, clampNumber(rawValue, min, max, fallback));
}
```

Template anchor:

```vue
<div class="manual-date-panel">
  <div class="manual-date-grid solar">
    <label class="manual-date-field">
      <input type="number" inputmode="numeric" min="1801" max="2099" :value="birthYear || 1989" @change="handleSolarManualInput('year', $event)" />
    </label>
    <label class="manual-date-field">
      <input type="number" inputmode="numeric" min="1" max="12" :value="birthMonth || 1" @change="handleSolarManualInput('month', $event)" />
    </label>
    <label class="manual-date-field">
      <input type="number" inputmode="numeric" min="1" max="31" :value="birthDay || 1" @change="handleSolarManualInput('day', $event)" />
    </label>
    <label class="manual-date-field">
      <input type="number" inputmode="numeric" min="0" max="23" :value="solarHour" @change="handleSolarManualInput('hour', $event)" />
    </label>
    <label class="manual-date-field">
      <input type="number" inputmode="numeric" min="0" max="59" :value="solarMinute" @change="handleSolarManualInput('minute', $event)" />
    </label>
  </div>
</div>
```

CSS anchor:

```css
.manual-date-panel {
  border: 1px solid #EEF2F7;
  border-radius: 16px;
  background: #F8FAFF;
  padding: 6px;
}

.manual-date-grid.solar,
.manual-date-grid.lunar {
  grid-template-columns: 1.25fr repeat(4, minmax(0, 1fr));
}

.manual-date-field {
  display: flex;
  min-width: 0;
  height: 36px;
  align-items: center;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  background: #FFFFFF;
  padding: 0 4px;
}

.manual-date-field input {
  min-width: 0;
  width: 100%;
  border: 0;
  background: transparent;
  color: #1F2937;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 11px;
  font-weight: 900;
  line-height: 1;
  outline: none;
  text-align: center;
}
```

### 5. Wheel Selection Must Auto-Sync

The user reported that wheel scroll changed visual position but did not commit selection until another tap. Local code fixes this by detecting the centered wheel value.

AI Studio must include equivalent behavior:

```ts
function centeredWheelValue(column: HTMLElement): string {
  const centerY = column.getBoundingClientRect().top + column.clientHeight / 2;
  const options = Array.from(column.querySelectorAll<HTMLElement>('.wheel-option'));
  const centered = options.reduce<HTMLElement | null>((nearest, item) => {
    if (!nearest) return item;
    const itemCenter = item.getBoundingClientRect().top + item.clientHeight / 2;
    const nearestCenter = nearest.getBoundingClientRect().top + nearest.clientHeight / 2;
    return Math.abs(itemCenter - centerY) < Math.abs(nearestCenter - centerY) ? item : nearest;
  }, null);
  return centered?.dataset.value || '';
}

function syncVisibleDateWheelSelection(): void {
  if (drawerKind.value !== 'datetime') return;
  if (drawerTab.value !== 'solar' && drawerTab.value !== 'lunar') return;
  const columns = Array.from(document.querySelectorAll<HTMLElement>('.drawer-sheet .wheel-frame .wheel-column'));
  const parts = ['year', 'month', 'day', 'hour', 'minute'];
  columns.slice(0, parts.length).forEach((column, index) => {
    const value = centeredWheelValue(column);
    if (value) applyWheelSelection(drawerTab.value, parts[index], value);
  });
}
```

`confirmDateDrawer()` must call `syncVisibleDateWheelSelection()` before applying and closing.

For solar mode, confirm should close immediately and refresh true solar preview in the background:

```ts
if (drawerTab.value === 'solar') {
  closeDrawer();
  void refreshTrueSolarPreview();
  return;
}
```

### 6. Location Data and True Solar Time

Backend/local knowledge changes:

- `features/four_pillars/knowledge/structured/birth-locations.json`
- `features/four_pillars/engine/solar_time.py`
- `features/four_pillars/knowledge/explicit-knowledge.md`

Local behavior:

- Default birth location is Beijing.
- Birth location has country/province/city/district, longitude, latitude, timezone, display name.
- True solar time is calculated from standard time plus longitude correction and equation of time.
- If no location is selected, use Beijing coordinates instead of showing `未校准`.

AI Studio does not need the full 83,988-line location dataset, but it must provide enough mock options to prove the picker is usable:

- Domestic: multiple provinces, multiple cities per province, multiple districts per city.
- Overseas: common countries and major cities/regions.
- Default: Beijing.
- Location picker should not collapse back to only `北京市东城区`.

### 7. Waiting Flow Stabilization

File:

- `product/frontend/src/components/four-pillars/FourPillarsAnalysis.vue`

The user reported generation getting stuck at phase 1 and then phase 4. Local behavior now:

- Enters waiting state immediately after submit.
- Starts the waiting animation while `submitFourPillarsReview(...).then(startReviewPolling)` is still pending.
- Allows result page to render once chart pillars are available, even before all long-form LLM text is completed.

Core readiness function:

```ts
function hasRenderableFourPillarsResult(review: FourPillarsReviewRecord | null): boolean {
  if (!review) return false;
  const chartDisplayPillars = review.chart_display?.pillars;
  if (chartDisplayPillars && Object.keys(chartDisplayPillars).length >= 4) {
    return true;
  }
  const chart = review.chart;
  if (chart && typeof chart === 'object') {
    const pillars = (chart as Record<string, unknown>).pillars;
    if (pillars && typeof pillars === 'object' && Object.keys(pillars as Record<string, unknown>).length >= 4) {
      return true;
    }
  }
  return false;
}
```

Use this in both `syncViewFromReview()` and `pollReviewUntilReady()`.

### 8. Natal Chart Header and More Chart Info Modal

File:

- `product/frontend/src/components/four-pillars/FourPillarsNatalTable.vue`

Top chart header:

- Left block: icon plus two lines, e.g. `男命` and `乾造`.
- Date block: calendar icon plus two lines.
- First line: `公历 1989-05-22 08:55`.
- Second line: `农历 1989-04-18 辰时`.
- Button text: `更多命盘信息`.

Compact lunar date helper:

```ts
const compactLunarDate = computed(() => {
  const raw = profile.value?.lunar_date || profile.value?.lunar_full_text || '';
  if (!raw) return '-';
  const match = raw.match(/(\d{4})年(?:闰)?(\d{1,2})月(\d{1,2})(?:日)?\s*([子丑寅卯辰巳午未申酉戌亥][时時])?/u);
  if (match) {
    return `${match[1]}-${pad2(match[2])}-${pad2(match[3])}${match[4] ? ` ${match[4].replace('時', '时')}` : ''}`;
  }
  return raw.replace(/^农历\s*/, '').replace(/年/g, '-').replace(/月/g, '-').replace(/日/g, ' ').replace(/\s+/g, ' ').trim();
});
```

The more-info modal is centered, not a bottom sheet:

- Max width around 360px.
- Max height 80vh.
- Internal scroll.
- Header: `更多命盘信息`.
- Combined info grid, no separate `基本信息` and `专业参数` section split.
- Includes 五行能量 progress bars.
- Includes 袁天罡称骨.

Info rows to support:

```text
姓名, 性别, 公历, 农历, 生肖, 出生地区, 出生节气, 星座, 星宿,
真太阳时, 胎元, 空亡, 命宫, 胎息, 身宫, 命卦
```

True solar display fallback:

```ts
const trueSolarTimeText = computed(() => {
  const explicit = String(profile.value?.true_solar_time_text || '').trim();
  if (explicit && explicit !== '未校准') return explicit;
  const effective = String(profile.value?.effective_birth_datetime || '').trim();
  const match = effective.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2})/u);
  if (match) return `${match[1]}-${match[2]}-${match[3]} ${match[4]}:${match[5]}`;
  return '按默认北京真太阳时校准';
});
```

### 9. Yuan Tiangang Bone Weight Display

Backend/local files:

- `features/four_pillars/knowledge/structured/yuan-tiangang-bone-weight.json`
- `features/four_pillars/engine/bone_weight.py`
- `features/four_pillars/engine/tests/test_bone_weight.py`

Frontend fields:

```ts
bone_weight?: {
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
} | null;
```

For `1989-05-22 08:55`, the UI should demonstrate the four-liang-one-qian result with this verse when applicable:

```text
此命推来事不同，为人能干亦凡庸
中年还有逍遥福，不比前时运未通
```

Verse formatting rule:

- If verse has four clauses, display first two clauses on line 1 and last two clauses on line 2.

Code anchor:

```ts
const boneWeightVerseLines = computed(() => {
  const verse = boneWeightVerse.value;
  if (!verse) return [];
  const clauses = verse.split(/[，,]/u).map((item) => item.trim()).filter(Boolean);
  if (clauses.length === 4) {
    return [`${clauses[0]}，${clauses[1]}`, `${clauses[2]}，${clauses[3]}`];
  }
  return [verse];
});
```

### 10. Type and Mock Data Requirements

AI Studio's mock `server.ts` must include enough data for the frontend to render all new states.

Required `chart_display.profile` fields:

```ts
{
  name,
  gender_label,
  structure_label,
  zodiac,
  solar_datetime_text,
  lunar_date,
  lunar_full_text,
  birth_place,
  timezone,
  solar_term_context,
  input_mode,
  standard_birth_datetime,
  effective_birth_datetime,
  true_solar_time,
  birth_location,
  true_solar_time_text,
  constellation,
  xiu,
  tai_yuan,
  tai_xi,
  ming_gong,
  shen_gong,
  life_gua,
  empty_branches_text,
  pillar_xun_kong_text,
  bone_weight
}
```

Required review readiness:

- Mock review can be `processing`, but once it has `chart_display.pillars`, the frontend should be able to display the result.
- Do not force the animation to wait forever for every text section.

Required location endpoint/mock:

- Return enough birth locations for domestic and overseas picker testing.
- Include default Beijing.
- Include more than one city/district.

## Do Not Change

- Do not change the real local API contracts beyond mock completion.
- Do not remove registered-user gating.
- Do not change points costs unless reading from existing config.
- Do not remove insufficient-points 402 behavior.
- Do not remove phone QiMen flows.
- Do not reintroduce the visible `四柱` input tab on the main input page.
- Do not use native browser date/time pickers.
- Do not show `未校准` for true solar time when default Beijing is available.

## Acceptance Checklist

- Phone and Four Pillars input pages have consistent title cards and CTA buttons.
- Four Pillars input page is compact.
- Date picker opens from bottom, not from left.
- Date picker is not covered by bottom nav.
- Solar/lunar picker shows manual numeric fields above wheel columns.
- Wheel scrolling commits the centered item automatically.
- Confirm in solar mode closes immediately.
- Location picker has usable domestic and overseas data, not only Beijing Dongcheng.
- Waiting animation does not get stuck at phase 1 or phase 4.
- Result page can render when a four-pillar chart is ready.
- Natal chart header uses compact sex/structure and solar/lunar date rows.
- Button says `更多命盘信息`.
- Modal shows combined chart info, five-element bars, true solar time, and Yuan Tiangang bone weight.
- Bone-weight verse displays in two lines when four clauses are available.
- Vue 3 + Vite build remains clean.
