# AI Studio Follow-Up Request: Fix H5 Preview Mock Runtime Robustness

The H5 test sandbox and demo account helper were added, and lint/build pass. However, the actual AI Studio preview is still not usable:

1. Home page shows `黄历数据加载失败`.
2. Clicking `AI Studio 演示账号极速通道` stays on `处理中` and does not successfully log in.

Please make a narrow runtime/testability repair. Do not redesign unrelated pages.

## Root Cause To Address

The project must be robust even if AI Studio still has this stale environment variable:

```text
VITE_API_BASE_URL=/api
```

That value is wrong for this codebase because `src/lib/api.ts` already calls paths such as:

```ts
requestJson('/api/v1/almanac/today')
requestJson('/api/v1/auth/phone/login')
```

If `VITE_API_BASE_URL=/api`, the browser requests:

```text
/api/api/v1/almanac/today
/api/api/v1/auth/phone/login
```

Those are wrong. They can fail or hang, causing both reported issues.

## Fix 1: Normalize API Base URL Defensively

In `src/lib/api.ts`, update `resolveApiBaseUrl()` so these values all resolve to an empty same-origin base:

```text
undefined
""
"/"
"/api"
"/api/"
```

Suggested logic:

```ts
function resolveApiBaseUrl(): string {
  const configuredValue = String(import.meta.env.VITE_API_BASE_URL || '').trim();
  const normalized = configuredValue.replace(/\/+$/, '');

  if (!normalized || normalized === '/api') {
    return '';
  }

  return normalized;
}
```

For this AI Studio H5 mock preview, all API calls should go to:

```text
/api/v1/...
```

never:

```text
/api/api/v1/...
```

## Fix 2: Remove Or Guard The Vite `/api` Proxy

Because `npm run dev` now runs `server.ts`, the Express custom server itself owns the mock `/api/v1/...` routes.

The Vite config still proxies `/api` to `http://127.0.0.1:8000`. That is dangerous in AI Studio because wrong `/api/api/...` paths can be forwarded away from the mock server.

Please remove the `/api` proxy for this AI Studio H5 mock project, or guard it so it is only used in a separate local backend mode.

The AI Studio preview should not depend on `127.0.0.1:8000`.

## Fix 3: Add Request Timeout So Buttons Do Not Spin Forever

In `src/lib/api.ts`, add a timeout to `requestJson()`.

Requirements:

- default timeout: 8000 ms
- if the request times out, throw `ApiError(408, 'request_timeout', null)` or a similarly clear error
- preserve support for existing `RequestInit.signal` if present
- make sure timers are cleared in `finally`

This prevents the demo login button from staying in `处理中` forever when a request is misrouted.

## Fix 4: Make Demo Login Helper Fail Visibly And Recover

In both demo login locations:

- `src/components/auth/AuthModal.vue`
- `src/components/home/Home.vue`

Ensure:

- clicking a demo account sets loading state
- successful login closes the modal/sandbox or clearly shows success
- failed login shows a visible error message
- timeout shows a visible error message such as `Mock API 请求超时，请检查 VITE_API_BASE_URL 是否为 / 或空值`
- loading state always resets in `finally`

Do not leave the button stuck on `处理中`.

## Fix 5: Make Almanac Failure Non-Sticky

In `src/components/home/Home.vue`:

- if `state.almanac` becomes non-null, immediately clear `almanacFailed`
- if retry succeeds, clear `almanacFailed`
- only show `黄历数据加载失败` after bootstrap/retry genuinely failed
- show the current effective API base/path in the H5 test sandbox so testers can spot `/api/api` misconfiguration quickly

Suggested Vue pattern:

```ts
watch(
  () => state.almanac,
  (value) => {
    if (value) {
      almanacFailed.value = false;
    }
  },
  { immediate: true },
);
```

## Fix 6: Actually Use `/api/v1/mock/summary`

The server added:

```text
GET /api/v1/mock/summary
```

Please add a small API helper and make the H5 test sandbox fetch it on open or on mount.

The sandbox should show:

- Mock API connected / failed
- demo account count
- almanac available
- runtime config available
- account coverage counts from the endpoint

If `/api/v1/mock/summary` fails, show the error. This will make mock API wiring visible instead of hidden.

## Fix 7: Verification Commands

After changes, verify:

```bash
npm run lint
npm run build
npm run dev
```

Then verify in preview/browser:

```text
GET /api/v1/almanac/today -> 200 JSON
GET /api/v1/mock/summary -> 200 JSON
POST /api/v1/auth/phone/status { phone: "13800138000" } -> registered true
POST /api/v1/auth/phone/login { phone: "13800138000", password: "Easewise123!" } -> access_token
```

Also verify there are no requests to:

```text
/api/api/v1/...
```

## Do Not Change

- Do not redesign the page layout.
- Do not add admin pages.
- Do not change Vue/Vite architecture.
- Do not remove the demo accounts.
- Do not reintroduce fantasy/game-style wording.
- Do not set `VITE_API_BASE_URL=/api`.

## Acceptance Checklist

- Home no longer shows `黄历数据加载失败` when the mock server is running.
- H5 test sandbox shows Mock API connected.
- Demo account quick login succeeds for `13800138000 / Easewise123!`.
- Failed mock requests time out with a visible message instead of spinning forever.
- Browser network requests use `/api/v1/...`, not `/api/api/v1/...`.
- `npm run lint` and `npm run build` pass.
