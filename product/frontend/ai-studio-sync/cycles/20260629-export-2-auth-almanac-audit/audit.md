# AI Studio Export 2 Auth And Almanac Audit

## Source

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise (2).zip`
- SHA256: `a77f765a31b9baf9ab0b6fed4a4032ab52b482bb7c8a03c2e83e8726775d0928`
- Clean extraction: `/tmp/easewise-export-2-clean`
- File count: `38`

## What Improved

- `npm run lint` passes after installing dependencies.
- `npm run build` passes.
- Fantasy/game-style terms from the prior export are largely removed from `src/` and `server.ts`.
- `src/types/api.ts` no longer has the duplicate-interface errors from export 1.
- Four Pillars input file grew from about 19 KB to 35 KB and now has more custom input UI than export 1.
- `server.ts` contains `/api/v1/almanac/today` and several auth/mock account endpoints.

## User-Observed Problems

The user reported:

1. Entering a phone number does not lead to login as expected.
2. Almanac/黄历 mock data is not visible.

These observations are consistent with the exported code.

## Root Causes

### 1. Mock server is not started by `npm run dev`

`server.ts` defines an Express custom server with Vite middleware and mock API routes, but `package.json` currently has:

```json
"dev": "vite --port=3000 --host=0.0.0.0"
```

That starts only Vite. It does not run `server.ts`.

So the frontend requests `/api/v1/...`, but the mock Express routes for auth, almanac, points, histories, etc. are not actually running in the AI Studio preview.

This explains why the user cannot see the almanac even though `server.ts` contains:

```ts
app.get("/api/v1/almanac/today", (req, res) => {
  res.json(almanacFallback);
});
```

### 2. `VITE_API_BASE_URL=/api` is wrong for this codebase

`src/lib/api.ts` already calls paths like:

```ts
requestJson('/api/v1/auth/phone/status', ...)
```

If `VITE_API_BASE_URL` is set to `/api`, the final URL becomes:

```text
/api/api/v1/auth/phone/status
```

Recommended values:

```text
VITE_API_BASE_URL=
VITE_APP_BASE_PATH=/
```

If AI Studio refuses an empty value, use:

```text
VITE_API_BASE_URL=/
VITE_APP_BASE_PATH=/
```

Because `resolveApiBaseUrl()` trims trailing slashes, `/` becomes an empty API base and requests still go to `/api/v1/...`.

### 3. Phone status response shape does not match frontend types

Frontend type:

```ts
export interface PhoneStatusResponse {
  registered: boolean;
  normalized_phone: string;
  next_action: 'login' | 'register';
}
```

`AuthModal.vue` checks:

```ts
if (status.registered) {
  mode.value = 'login';
} else {
  mode.value = 'register';
}
```

But `server.ts` currently returns:

```ts
res.json({ status: isRegistered ? "registered" : "not_registered" });
```

That means the frontend never receives `registered: true`, so registered demo accounts can be routed incorrectly.

### 4. Custom server cannot be run through the current script setup

`server.ts` is TypeScript. The package does not include a script like:

```json
"dev": "tsx server.ts"
```

and does not include `tsx` as a dependency/devDependency. AI Studio needs a single command that runs the Express mock server and Vite middleware together.

## Recommended Fix

Ask AI Studio to:

1. Change the development command to run the custom server, not plain Vite.
2. Add `tsx` if needed.
3. Keep `server.ts` serving both mock APIs and Vite middleware on one origin.
4. Fix `/api/v1/auth/phone/status` response shape.
5. Clarify env vars in `.env.example` / README.

## Verification Performed

- Clean zip extraction completed.
- `npm install` was run in a temporary copy for verification only.
- `npm run lint` passed.
- `npm run build` passed.
- Static inspection confirmed the auth response mismatch and dev-script/server mismatch.
