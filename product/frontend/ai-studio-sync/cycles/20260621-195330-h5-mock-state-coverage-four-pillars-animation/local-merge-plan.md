# Local Merge Plan

Status: `planned-only`

This cycle does not apply any AI Studio output to local source. The next step is for the user to submit `prompt.md` plus `bundle.md` to AI Studio, download the next zip, and register it.

## After Next AI Studio Zip

1. Register the new AI Studio zip under `.aistudio-sync/aistudio-latest/`.
2. Diff the new export against local `product/frontend`.
3. Confirm the export remains Vue 3 + Vite and does not introduce React/TSX.
4. Check `server.ts` mock coverage for the required demo users and states.
5. Check `FourPillarsAnalysis.vue` for the restored `sleep(ms)` helper and local error mapping.
6. Check that phone and four pillars POST/GET flows stage progress instead of instantly completing.
7. Only then evaluate whether any visual/state presentation should be merged into the local Vue frontend.

## Likely Local Merge Candidates Later

Only if the next export improves them without changing behavior:

- waiting-state visual refinements in `Analysis.vue`
- waiting-state visual refinements in `FourPillarsAnalysis.vue`
- profile/history/ledger state presentation in `Profile.vue`
- auth modal microcopy/layout if it preserves local mode/focus/error behavior

## Non-Candidates

Do not merge:

- AI Studio mock server code into production backend
- AI Studio-invented product behavior
- AI Studio-invented field names or aspect keys
- profile/auth rewrites that remove local flows
- any React/TSX artifacts
