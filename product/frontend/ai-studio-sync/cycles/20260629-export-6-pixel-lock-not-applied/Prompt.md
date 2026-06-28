# AI Studio Phase A Pixel-Lock Request

The previous pixel-lock request was not applied. The latest export worked on the AI Agent session engine, but the two core assessment pages are still the old simplified AI Studio versions.

This pass must be **Phase A only**:

1. 手机号评测
2. 四柱八字

Do not work on AI Agent in this pass.
Do not work on Profile in this pass.
Do not do general design optimization in this pass.

## Why This Is Required

The latest export still has these structural gaps:

```text
src/components/analysis/Analysis.vue
  Current AI Studio: ~573 lines
  Local source:       ~2884 lines

src/components/four-pillars/FourPillarsAnalysis.vue
  Current AI Studio: ~658 lines
  Local source:       ~3765 lines
```

This means the current AI Studio files are simplified replacements, not pixel-level replications.

## Source Of Truth

The `bundle.md` I will paste after this prompt is the source of truth for Phase A.

For every file included in `bundle.md`:

1. Recreate the file at the exact path shown.
2. Replace the current AI Studio file content with the bundled content.
3. Do not summarize.
4. Do not shorten.
5. Do not redesign.
6. Do not keep the current simplified AI Studio component if the bundle contains a replacement.

## Required Files To Replace

Replace these files from `bundle.md`:

```text
src/App.vue
src/components/analysis/Analysis.vue
src/components/four-pillars/FourPillarsAnalysis.vue
src/components/four-pillars/FourPillarsNatalTable.vue
src/components/support/ContactServiceModal.vue
src/composables/useEaseWiseApp.ts
src/lib/api.ts
src/types/api.ts
src/config/pricing.ts
src/constants/storage.ts
src/index.css
```

## Preserve Runtime Mock Fixes

After replacing the bundled files, preserve or re-apply these existing AI Studio mock/runtime fixes if needed:

- `npm run dev` should continue to run `tsx server.ts`.
- `tsx` should remain in `devDependencies`.
- `VITE_API_BASE_URL=/api` must not create `/api/api/v1/...` requests.
- requests should timeout visibly instead of spinning forever.
- `/api/v1/mock/summary` may remain as mock-only test helper.
- demo accounts in `server.ts` should remain usable.

If replacing `src/lib/api.ts` removes a mock-helper function you added, re-add it minimally without changing the bundled assessment page logic.

## Mock Compatibility Requirement

Make the mock server satisfy the restored bundled frontend files.

Demo accounts must work:

```text
13800138000 / Easewise123! - full regression / rich history / high points
13600136000 / Easewise123! - low points / unlock insufficient
13500135000 / Easewise123! - very low points / base insufficient
13900139000 / Easewise123! - high points / empty history
13700137000 / Easewise123! - mixed partial history
```

For Phase A, verify at minimum:

- phone review history list loads for `13800138000`
- phone review detail can open
- phone review generation does not hang
- Four Pillars history list loads for `13800138000`
- Four Pillars detail can open
- Four Pillars generation does not hang
- insufficient-points state can be triggered by `13500135000` or `13600136000`

## Do Not Change

- Do not work on AI Agent in this pass.
- Do not work on Profile in this pass.
- Do not redesign Home.
- Do not add admin pages.
- Do not convert Vue/Vite architecture.
- Do not replace bundled files with shorter simplified versions.
- Do not remove existing demo accounts.
- Do not reintroduce fantasy/game-style wording.

## Hard Acceptance Gate

Your response and export will be judged by file replacement, not by written claims.

The next export fails if:

- `src/components/analysis/Analysis.vue` remains around 573 lines.
- `src/components/four-pillars/FourPillarsAnalysis.vue` remains around 658 lines.
- you primarily change AI Agent, Profile, or Home instead of the two assessment pages.

The next export passes Phase A only if:

- `Analysis.vue` is structurally close to the bundled local source.
- `FourPillarsAnalysis.vue` is structurally close to the bundled local source.
- `FourPillarsNatalTable.vue` matches the bundled local source.
- `npm run lint` passes.
- `npm run build` passes.
- `npm run dev` starts the mock server.
- phone review and Four Pillars flows can be tested with demo accounts.

## Response Format

Reply with:

1. Exact files replaced from `bundle.md`.
2. Minimal compatibility edits made after replacement.
3. Runtime/mock fixes preserved or re-applied.
4. Verification results for `npm run lint`, `npm run build`, and `npm run dev`.
5. Line counts for:
   - `src/components/analysis/Analysis.vue`
   - `src/components/four-pillars/FourPillarsAnalysis.vue`
   - `src/components/four-pillars/FourPillarsNatalTable.vue`
