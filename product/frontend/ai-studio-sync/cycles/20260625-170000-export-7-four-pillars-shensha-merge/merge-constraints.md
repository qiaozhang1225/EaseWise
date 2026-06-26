# Export 7 Merge Constraints

## Preserve Local Runtime Truth
- Keep local `submitFourPillarsReview`, `refreshCurrentFourPillarsReview`, polling, error handling, insufficient-points states, aspect unlocks, and luck generation.
- Keep export 6 local merges for AI Agent bottom alignment, profile combined review history, and Four Pillars staged waiting animation.
- Treat AI Studio as the visual/design source and local repository as the business/runtime source.

## Narrow Merge Boundary
- Merge only Four Pillars table display changes from AI Studio export 7.
- Do not replace whole files where AI Studio includes mock or older flow assumptions.
- Do not merge `server.ts` into product source.

## Visual Acceptance
- Shen Sha row label uses the same typography and tone as `地势`, `自坐`, `旬空`, and `纳音`.
- Expand/collapse affordance is arrow-only and sits below the `神煞` label.
- Collapsed columns show two shen-sha names plus `+N 更多` when overflow exists.
- Shen Sha items render as table text, not colored pills or badges.
