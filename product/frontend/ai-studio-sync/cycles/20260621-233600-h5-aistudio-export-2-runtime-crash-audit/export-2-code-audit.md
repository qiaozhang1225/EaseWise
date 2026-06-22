# AI Studio Export 2 Code Audit

Cycle: `20260621-233600-h5-aistudio-export-2-runtime-crash-audit`

Source zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (2).zip`

SHA256: `a24f18342acd99153da003fe490beeffda1084734d9c85d046030f299eb49da4`

## Summary

The latest AI Studio export did not complete the previous mock/state coverage prompt. It only made a narrow runtime-crash fix in `src/components/four-pillars/FourPillarsAnalysis.vue`.

The crash message reported by the user, `Cannot read properties of undefined (reading 'some')`, was partially addressed by adding defensive checks around `cycle.year_items` in the luck-cycle/year selector UI. This is a useful patch, but the main sync goals are still largely unexecuted.

## What Changed From Previous AI Studio Export

AI Studio changed exactly one text file:

- `src/components/four-pillars/FourPillarsAnalysis.vue`

No changes were made to:

- `server.ts`
- `src/components/analysis/Analysis.vue`
- `src/components/ai-agent/AIAgent.vue`
- `src/components/profile/Profile.vue`
- `src/components/auth/AuthModal.vue`
- `src/types/api.ts`
- `src/lib/api.ts`

This means the previous prompt's main requirements around mock data, staged generation, demo accounts, phone aspects, and profile/history coverage did not run.

## What Was Actually Fixed

### Luck Year Selector Null Guard

AI Studio changed the active luck-cycle watcher from an unconditional `cycle.year_items.some(...)` to a guarded branch:

```ts
const cycle = cycles.find((item) => item.cycle_key === activeCycleKey.value) || cycles[0];
if (cycle && cycle.year_items) {
  if (!cycle.year_items.some((item) => item.year === selectedLuckYear.value)) {
    selectedLuckYear.value = cycle.year_items.find((item) => item.is_current)?.year || cycle.year_items[0]?.year || null;
  }
} else {
  selectedLuckYear.value = null;
}
```

### Luck Render Lookup Null Guard

AI Studio changed:

```ts
return cycle.year_items.find((item) => item.year === render.year)?.render || null;
```

to:

```ts
return cycle.year_items?.find((item) => item.year === render.year)?.render || null;
```

### Flow-Year Selector Visibility Guard

AI Studio changed the flow-year selector to render only when `selectedLuckCycle.year_items` exists and has length:

```vue
<div v-if="selectedLuckCycle && selectedLuckCycle.year_items && selectedLuckCycle.year_items.length" class="grid grid-cols-[34px_1fr]">
```

These changes match the user's crash report and should reduce the specific `.some` runtime crash.

## Still Not Fixed

### 1. `sleep` Helper Is Still Missing

The latest AI Studio `FourPillarsAnalysis.vue` still calls `sleep(...)` in three places:

- `await sleep(ASPECT_UNLOCK_RETRY_DELAY_MS)`
- `await sleep(REVIEW_READY_RETRY_DELAY_MS)`
- `await sleep(LUCK_RENDER_RETRY_DELAY_MS)`

But it still does not define:

```ts
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
```

Local has this helper. AI Studio has not restored it.

Impact: any path that reaches polling, aspect unlock wait, or luck render wait can still crash at runtime with `sleep is not defined`.

### 2. Mock Server Still Completes Immediately

`server.ts` did not change.

Phone review creation still returns:

```ts
status: "completed",
progress_stage: "completed",
```

Four pillars creation still returns:

```ts
status: "completed",
```

There is still no staged transition:

```text
queued -> scoring -> rendering -> finalizing -> completed
```

Impact: four pillars waiting animation can still appear missing because the mock response completes immediately.

### 3. Required Demo Accounts Are Missing

Expected from previous prompt:

- `13800138000 / Easewise123!`
- `13900139000 / Easewise123!`
- `13700137000 / Easewise123!`

Actual latest `server.ts`:

- `13800138000`: present
- `13900139000`: missing
- `13700137000`: missing

Impact: low-points and empty-history UI states still cannot be tested.

### 4. Phone Mock Aspects Are Still Incomplete

Expected local phone aspect keys:

- `career`
- `wealth`
- `love`
- `health`
- `acad`
- `fortune`
- `investment`
- `travel`
- `social`
- `family`
- `personality`
- `fengshui`

Actual latest `server.ts` phone aspect keys:

- `career`
- `finance`
- `love`

`wealth` is still missing, and `finance` is still incorrectly used.

Impact: the phone result cannot display the full local 12-aspect grid, and the key mismatch still risks UI fallback/incorrect label behavior.

### 5. Four Pillars Mock Aspects Are Still Incomplete

Expected four pillars aspect examples:

- `personality`
- `career`
- `wealth`
- `love`
- `health`
- `family_environment`

Actual latest `server.ts` four pillars aspect keys include:

- `day_master`
- `career_trend`
- `wealth_analysis`
- `wealth_capacity`

Impact: the four pillars result still does not exercise the local target result layout.

### 6. Four Pillars Error Mapping Is Still Simplified

Latest AI Studio still has:

```ts
function handleReviewSyncError(error: unknown): void {
  if (error instanceof ApiError) {
    if (error.status === 402) {
      setError('insufficient_points');
      return;
    }
    if (error.status === 403 && error.detail === 'module_disabled') {
      setError('module_disabled');
      return;
    }
  }
  setError('review_failed', humanizeError(error));
}
```

Still missing local distinctions:

- `birth_datetime`
- `review_timeout`
- `request_failed`

Impact: the user can still see misleading or over-generic four pillars error states.

### 7. AI Agent / Qimen Drift Still Exists

`src/components/ai-agent/AIAgent.vue` did not change.

It remains substantially different from local:

- local similarity: `8.19%`
- AI Studio version is still direct API chat oriented
- local version is login-gated and persists conversation to localStorage

Impact: "奇门问事" behavior is not yet aligned.

## Similarity Snapshot

| file | similarity | status |
|---|---:|---|
| `src/App.vue` | 100.00% | aligned |
| `src/components/home/Home.vue` | 99.93% | aligned |
| `src/index.css` | 100.00% | aligned |
| `src/composables/useEaseWiseApp.ts` | 100.00% | aligned |
| `src/lib/api.ts` | 99.59% | close |
| `src/types/api.ts` | 95.31% | close |
| `src/components/analysis/Analysis.vue` | 51.54% | still simplified |
| `src/components/four-pillars/FourPillarsAnalysis.vue` | 86.70% | crash patch only; still missing helper/error mapping |
| `src/components/profile/Profile.vue` | 5.23% | still rewritten |
| `src/components/auth/AuthModal.vue` | 12.85% | still rewritten |
| `src/components/support/ContactServiceModal.vue` | 13.61% | still rewritten |
| `src/components/ai-agent/AIAgent.vue` | 8.19% | still drifted |
| `src/components/recharge/RechargePage.vue` | 4.19% | still not aligned |
| `src/components/points-claim/PointsClaimPage.vue` | 4.39% | still not aligned |

## Build Verification

I installed dependencies inside the extracted AI Studio export directory only and ran:

```bash
npm run lint
npm run build
```

Both commands completed successfully. Temporary `node_modules` and `dist` generated for verification were removed afterward.

Important nuance: successful build does not prove runtime paths are safe. The missing `sleep` helper is still visible by static inspection and can still fail when polling/unlock paths execute.

## Execution Progress Assessment

AI Studio appears to have stopped after a runtime-crash hotfix.

Estimated progress against the previous prompt:

- Vue/Vite architecture preserved: done
- `.some` crash around missing `year_items`: partially fixed
- `sleep(ms)` helper restored: not done
- staged phone generation: not done
- staged four pillars generation: not done
- 3 demo accounts: not done
- low-points account: not done
- empty-history account: not done
- phone 12 aspects: not done
- `wealth` key instead of `finance`: not done
- four pillars rich mock data: not done
- luck cycle/year statuses and result bodies: not done
- local four pillars error mapping: not done
- AI Agent/Qimen local behavior: not done
- profile/history/ledger coverage: not done

## Recommended Next Step

Do not treat this export as ready for local design merge.

The next AI Studio prompt should be even narrower and should explicitly say:

1. Keep the `.some` crash fix.
2. First add the missing `sleep(ms)` helper.
3. Then modify `server.ts`; do not stop after `FourPillarsAnalysis.vue`.
4. Add the two missing demo accounts.
5. Add staged mock progress for phone and four pillars.
6. Replace phone `finance` with local key `wealth`.
7. Add all 12 phone aspects.
8. Add enough four pillars `luck_analysis.cycles[].year_items` data so the new guards do not hide the whole flow-year UI.
9. Restore local error mapping.
