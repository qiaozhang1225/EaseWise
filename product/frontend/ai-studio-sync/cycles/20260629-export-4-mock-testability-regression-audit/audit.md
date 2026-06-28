# AI Studio Export 4 Mock Testability Regression Audit

## Source

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise (4).zip`
- SHA256: `c8c280fdf64cef2a95e818e464d8e52655f8bb6cfbe4abeefba4c6501680654d`
- Clean extraction: `/tmp/easewise-export-4-fresh`
- File count: `39`

## User-Observed Issues

1. Home page shows `黄历数据加载失败`.
2. Clicking `AI Studio 演示账号极速通道` keeps showing `处理中` and does not finish login.

## What Export 4 Added

- `AuthModal.vue` now has a demo account helper.
- `Home.vue` now has a floating `H5测试沙盒`.
- `server.ts` now has `GET /api/v1/mock/summary`.
- `server.ts` still has `GET /api/v1/almanac/today`.
- `npm run lint` passes.
- `npm run build` passes.

## Runtime Verification

The exported mock server works when requests hit the correct `/api/v1/...` routes.

In a temporary copy only, `server.ts` was patched to run on port `3304` to avoid the local port `3000` conflict.

Verified:

```text
GET  /api/v1/almanac/today             -> 200 JSON
POST /api/v1/auth/phone/login          -> 200 JSON for 13800138000 / Easewise123!
```

But the wrong double-prefix route fails:

```text
GET  /api/api/v1/almanac/today         -> 404 / proxy fallback
POST /api/api/v1/auth/phone/login      -> 404 / proxy fallback
```

## Root Cause

The likely shared cause is that AI Studio still has `VITE_API_BASE_URL=/api` configured from the previous iteration, or the code does not defensively normalize that bad value.

Current `src/lib/api.ts` builds requests as:

```ts
fetch(`${API_BASE_URL}${path}`)
```

and all API paths already include `/api/v1`, for example:

```ts
requestJson('/api/v1/almanac/today')
requestJson('/api/v1/auth/phone/login')
```

So if `VITE_API_BASE_URL=/api`, the final request becomes:

```text
/api/api/v1/almanac/today
/api/api/v1/auth/phone/login
```

The custom Express server does not define `/api/api/v1/...`. In development, Vite middleware/proxy can then route the bad `/api/api/...` request toward `127.0.0.1:8000`, which is not the mock server. In AI Studio this can fail or hang, producing exactly:

- almanac failure
- demo login spinner stuck in `处理中`

## Secondary Frontend Robustness Issues

### 1. No request timeout

`requestJson()` has no timeout. If a bad proxy target hangs, login buttons can remain in processing state for a long time.

### 2. Home almanac failed state is sticky

`Home.vue` sets `almanacFailed = true` after bootstrap if `state.almanac` is missing, but it should also clear failure when almanac later loads successfully.

### 3. Mock summary endpoint is not actually consumed

`server.ts` exposes `/api/v1/mock/summary`, but the current frontend sandbox mostly uses hard-coded `demoAccounts` and `state.almanac` / `state.runtimeConfig`. It does not appear to fetch and display the mock summary endpoint as the source of truth.

## Recommended Next Fix

Ask AI Studio to make the app robust even if the environment variable is still accidentally set to `/api`:

1. Normalize `VITE_API_BASE_URL` in `resolveApiBaseUrl()` so `''`, `'/'`, and `'/api'` all resolve to an empty base for this mock H5 project.
2. Remove or disable the Vite `/api` proxy while using the Express custom server, or at least do not proxy `/api/api/...` to `127.0.0.1:8000`.
3. Add an 8-second request timeout to `requestJson()` so UI buttons never spin forever.
4. In `Home.vue`, clear `almanacFailed` when `state.almanac` becomes non-null, and make retry call the correct API path.
5. In the demo login helper, always reset `submitting` and show a visible error if login fails or times out.
6. Make the sandbox fetch `/api/v1/mock/summary` and show whether that endpoint is connected.

## Status

Export 4 is structurally close, but AI Studio preview can still be unusable if the env/base path is wrong. The next prompt should be a defensive runtime/testability repair, not a design pass.
