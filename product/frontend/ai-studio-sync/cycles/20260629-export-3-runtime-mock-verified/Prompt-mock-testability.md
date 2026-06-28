# AI Studio Follow-Up Request: Make Mock Data Testable In The H5 Preview

The runtime wiring is now fixed: `npm run dev` starts `server.ts`, auth endpoints work, almanac endpoint works, and lint/build pass. However, the AI Studio preview is still hard to test because the mock data is not exposed as a clear frontend testing workflow.

Please make a narrow mock-data and testability pass. Do not redesign unrelated screens.

## Goal

Make the AI Studio H5 preview fully testable without reading `server.ts`.

A tester should be able to:

1. See which demo accounts exist.
2. Log in quickly with a demo account.
3. Verify almanac/黄历 data is loaded.
4. Open phone review history.
5. Open Four Pillars history.
6. Test empty states.
7. Test low-points and insufficient-points states.
8. Test locked and unlocked aspect states.
9. Test recharge/points ledger/profile states.

## Fix 1: Add A Demo Account Helper In The Login Modal

In `src/components/auth/AuthModal.vue`, add a compact demo account helper when running in the AI Studio/mock preview.

It should show 5 selectable demo accounts:

```text
13800138000 / Easewise123! - full regression, rich history, high points
13600136000 / Easewise123! - low points, can create base review, insufficient for deep unlocks
13500135000 / Easewise123! - very low points, insufficient for base generation
13900139000 / Easewise123! - high points, empty history
13700137000 / Easewise123! - high points, mixed partial-history test account
```

Interaction:

- Tapping an account fills the phone and password fields.
- If possible, also offer a one-tap `登录此演示账号` button.
- Keep the UI compact and professional.
- Do not expose this as a production feature. It is for AI Studio/mock preview testing only.

Implementation options:

- Simple: always show the helper in this AI Studio prototype.
- Better: show it when `import.meta.env.DEV` is true or when `VITE_ENABLE_DEMO_ACCOUNTS !== 'false'`.

## Fix 2: Add A Mock Data Health Panel Or Lightweight Status

Add a small, non-intrusive mock status entry in the H5 preview, preferably on the home page or login modal:

```text
Mock API: connected
Almanac: loaded
Demo accounts: 5
```

This should be based on real frontend state/API results where possible:

- almanac loaded from `state.almanac`
- runtime config loaded from `state.runtimeConfig`
- auth status endpoint available from test calls or a dedicated mock summary endpoint

Keep it visually small. This is a testability aid, not a product marketing block.

## Fix 3: Add A Dedicated Mock Summary Endpoint

In `server.ts`, add:

```text
GET /api/v1/mock/summary
```

Return a concise JSON payload:

```json
{
  "demo_accounts": [
    {
      "phone": "13800138000",
      "password": "Easewise123!",
      "label": "Full regression / high points",
      "points": 20000,
      "phone_history_count": 2,
      "four_pillars_history_count": 2,
      "points_ledger_count": 8,
      "recommended_tests": ["phone history", "four pillars history", "aspect unlock", "luck cycles", "profile", "recharge"]
    }
  ],
  "almanac_available": true,
  "runtime_config_available": true
}
```

Use this endpoint only for mock/demo test visibility.

## Fix 4: Enrich Mock Account Coverage

Current mock data is still uneven. Please make the seeded accounts cover these states:

### 13800138000 - Full Regression

Must include:

- at least 2 phone review history records
- at least 2 Four Pillars history records
- unlocked and locked phone aspects
- unlocked and locked Four Pillars aspects
- completed luck cycle render
- completed flowing-year render
- points ledger with recharge, base review deductions, aspect unlock deductions, luck-cycle/year deductions
- profile data filled enough for personal center

### 13600136000 - Low Points

Must include:

- enough points for base review only
- insufficient points on aspect unlock
- insufficient points on luck cycle/year generation
- at least 1 existing phone or Four Pillars history record so history UI can be tested

### 13500135000 - Very Low Points

Must include:

- insufficient points before base phone review
- insufficient points before base Four Pillars review
- points ledger showing small starting balance

### 13900139000 - Empty State

Must include:

- high points
- no phone history
- no Four Pillars history
- empty-state UI should be testable
- first-generation flow should be testable

### 13700137000 - Mixed Partial State

This account should not be empty. It should include:

- 1 phone review
- 1 Four Pillars review
- some aspects unlocked and some locked
- a few points ledger rows
- enough high points to continue testing

## Fix 5: Ensure Frontend Histories Refresh After Demo Login

After login succeeds, the frontend should refresh:

- current user
- points
- points ledger
- phone review history
- Four Pillars history
- almanac/runtime config if needed

If this already happens, verify it with the demo accounts and fix any missed state updates.

## Fix 6: Almanac Visibility

The home page currently has an almanac section, but testers may not know whether it is mock-loaded.

Please ensure:

- when `/api/v1/almanac/today` succeeds, the home page visibly displays the returned mock date/yi/ji/ganzhi data
- if almanac fails, show a compact error/fallback state instead of silent loading text
- the mock summary/status panel indicates almanac loaded

## Do Not Change

- Do not add admin management pages.
- Do not replace Vue/Vite architecture.
- Do not change real API route names except adding the mock-only `/api/v1/mock/summary`.
- Do not set `VITE_API_BASE_URL=/api`.
- Do not remove the professional terminology cleanup.
- Do not reintroduce fantasy/game-style wording.
- Do not redesign the Four Pillars page in this pass.

## Acceptance Checklist

- `npm run lint` passes.
- `npm run build` passes.
- `npm run dev` starts the custom Express/Vite mock server.
- Login modal shows demo account options.
- Tapping `13800138000` can log in with `Easewise123!`.
- After logging in as `13800138000`, phone history, Four Pillars history, points ledger, profile, and almanac data are visible.
- `13900139000` clearly shows empty history states but has enough points to generate new tests.
- `13500135000` clearly triggers insufficient-points states.
- `/api/v1/mock/summary` returns demo account coverage information.
- Home page visibly shows loaded almanac/黄历 mock data or an explicit fallback/error state.
