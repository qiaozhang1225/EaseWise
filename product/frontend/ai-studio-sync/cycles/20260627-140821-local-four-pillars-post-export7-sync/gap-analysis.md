# Gap Analysis For AI Studio

## Current Gap

AI Studio export 7 covered part of the Four Pillars shen-sha and luck-analysis table alignment, but it predates the latest local product work.

The main gaps are:

1. AI Studio does not yet have the latest compact Four Pillars input design.
2. AI Studio may still use incomplete picker behavior or insufficient location data.
3. AI Studio does not yet mirror the manual numeric date fields above the wheels.
4. AI Studio may still block result rendering until full completion instead of rendering when chart pillars exist.
5. AI Studio may not have the latest `更多命盘信息` modal fields and bone-weight display.
6. AI Studio mock `server.ts` likely lacks the expanded profile fields and rich chart data required by the current local frontend.

## Highest-Risk Areas

### Date Picker

This is the most sensitive area because the user rejected two previous directions:

- Left-side drawer is wrong.
- Native date/time input is wrong.

The correct solution is a bottom sheet with separate manual numeric fields plus wheel selectors.

### Waiting Flow

The user has already hit stuck states in deployed testing:

- Stage 1 stuck.
- Stage 4 stuck.

AI Studio should copy the readiness rule from local code:

```text
Renderable chart exists -> show result.
Full text can continue or be absent in mock.
```

### Birth Location

The user tested on LAN and saw only `北京市东城区`, which is not acceptable. Even if AI Studio cannot carry the full local dataset, the prototype must include enough realistic domestic and overseas rows to test the picker.

### Bone Weight

The user specifically wanted the verse visible. A short `格局` summary alone is insufficient.

For four-liang-one-qian, show:

```text
此命推来事不同，为人能干亦凡庸
中年还有逍遥福，不比前时运未通
```

## Recommended AI Studio Implementation Order

1. Update `FourPillarsAnalysis.vue` input card and CTA.
2. Fix bottom-sheet container and navigation offset.
3. Add manual numeric date fields and wheel auto-sync.
4. Expand location mock data.
5. Stabilize waiting/result readiness.
6. Update `FourPillarsNatalTable.vue` header and modal.
7. Expand `server.ts` mock profile/chart fields.
8. Run build and test the main four browser scenarios.
