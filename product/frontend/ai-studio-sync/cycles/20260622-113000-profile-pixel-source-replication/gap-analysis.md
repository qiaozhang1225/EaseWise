# Gap Analysis

- Local frontend root: `product/frontend`
- AI Studio extracted root: `.aistudio-sync/aistudio-latest/extracted`
- Local text files: 35
- AI Studio text files: 34
- Shared relative paths: 33

## Local Files Missing In AI Studio

- `public/e19114aa64052dc2b995091d81770fc8.txt`
- `src/components/admin/AdminSelect.vue`

## AI Studio Files Not Present Locally

- `server.ts`

## Local Pages And Views

- `product/frontend/src/App.vue`
- `product/frontend/src/components/points-claim/PointsClaimPage.vue`
- `product/frontend/src/components/recharge/RechargePage.vue`

## AI Studio Pages And Views

- `src/App.vue`
- `src/components/points-claim/PointsClaimPage.vue`
- `src/components/recharge/RechargePage.vue`

## Local Behavior Sources To Preserve

- `product/frontend/src/components/auth/AuthModal.vue`
- `product/frontend/src/components/support/ContactServiceModal.vue`
- `product/frontend/src/lib/api.ts`
- `product/frontend/src/types/api.ts`

## AI Studio Behavior-Like Sources To Treat As Mock Or Prototype Logic

- `src/components/auth/AuthModal.vue`
- `src/components/support/ContactServiceModal.vue`
- `src/lib/api.ts`
- `src/types/api.ts`

## State Signal Comparison

- Local: `{'empty': 3, 'auth': 12, 'login': 8, 'permission': 1, 'disabled': 11, 'loading': 7, 'error': 13, 'payment': 5, 'expired': 3, 'invalid': 3, 'success': 3}`
- AI Studio: `{'auth': 10, 'permission': 1, 'empty': 2, 'error': 13, 'success': 5, 'disabled': 10, 'login': 7, 'payment': 5, 'invalid': 3, 'loading': 6, 'expired': 1}`

## Next Iteration Guidance

- Keep already aligned shared files and visible flows stable.
- Ask AI Studio to close the local-only gaps that matter for the selected slice.
- Treat AI Studio-only files as design suggestions unless the local repo has matching behavior.
- Preserve every local behavior source listed above during local merge.
