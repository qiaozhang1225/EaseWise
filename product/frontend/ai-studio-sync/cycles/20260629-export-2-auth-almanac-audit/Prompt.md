# AI Studio Follow-Up Request

The latest export is much closer and passes both `npm run lint` and `npm run build`, but the preview still does not behave correctly because the mock server is not wired into the AI Studio runtime and the phone auth response shape does not match the frontend contract.

Please make a narrow repair pass. Do not redesign unrelated pages.

## Fix 1: Run the Custom Mock Server in Development

Current `package.json` starts plain Vite:

```json
"dev": "vite --port=3000 --host=0.0.0.0"
```

This is not enough, because the mock APIs are in `server.ts`. The preview needs to run the Express custom server, which already mounts Vite middleware and defines mock endpoints.

Please update the project so `npm run dev` starts `server.ts`.

Recommended approach:

```json
"scripts": {
  "dev": "tsx server.ts",
  "dev:vite": "vite --port=3000 --host=0.0.0.0",
  "build": "vite build",
  "preview": "vite preview",
  "clean": "rm -rf dist server.js",
  "lint": "tsc --noEmit"
}
```

Add `tsx` to devDependencies if needed.

The goal: AI Studio preview should serve the H5 app and the mock API routes from the same origin, so `/api/v1/...` works without a separate backend.

## Fix 2: Correct Environment Variable Guidance

Do **not** set `VITE_API_BASE_URL=/api` for this project. The API paths already include `/api/v1`, so that produces invalid `/api/api/v1/...` URLs.

Use:

```text
VITE_API_BASE_URL=
VITE_APP_BASE_PATH=/
```

If AI Studio refuses an empty value, use:

```text
VITE_API_BASE_URL=/
VITE_APP_BASE_PATH=/
```

Please update `.env.example` and README comments to make this clear.

## Fix 3: Match Phone Status Response Contract

Frontend expects:

```ts
export interface PhoneStatusResponse {
  registered: boolean;
  normalized_phone: string;
  next_action: 'login' | 'register';
}
```

`AuthModal.vue` checks `status.registered`.

But `server.ts` currently returns:

```ts
{ status: "registered" }
```

Please change `/api/v1/auth/phone/status` to return:

```ts
const normalizedPhone = String(phone || '').trim();
const isRegistered = Boolean(usersMock[normalizedPhone]);
res.json({
  registered: isRegistered,
  normalized_phone: normalizedPhone,
  next_action: isRegistered ? "login" : "register",
});
```

Then verify:

- `13800138000` returns `registered: true`
- `13600136000` returns `registered: true`
- `13500135000` returns `registered: true`
- `13900139000` returns `registered: true`
- `13700137000` returns `registered: true`
- an unknown valid phone returns `registered: false`

All seeded demo account passwords should remain:

```text
Easewise123!
```

## Fix 4: Verify Almanac Mock Is Visible

`server.ts` already has `/api/v1/almanac/today`, but it is not visible if `server.ts` is not running.

After Fix 1, verify:

```text
GET /api/v1/almanac/today
```

returns the `almanacFallback` JSON.

The H5 home page should be able to load and display the almanac/黄历 data through the existing app bootstrap flow.

## Fix 5: Keep The Current Improvements

Preserve:

- current professional terminology cleanup
- expanded mock account data
- Four Pillars manual + wheel input work
- location picker work
- true solar time preview work
- passing `npm run lint`
- passing `npm run build`

## Do Not Change

- Do not add admin management pages.
- Do not convert the project to another framework.
- Do not change frontend route names or component event contracts.
- Do not set `VITE_API_BASE_URL=/api`.
- Do not remove the mock account personas.
- Do not reintroduce fantasy-style wording.

## Acceptance Checklist

- `npm install` succeeds.
- `npm run lint` passes.
- `npm run build` passes.
- `npm run dev` starts the custom Express/Vite server successfully.
- In the AI Studio preview, `/api/v1/almanac/today` returns JSON.
- In the AI Studio preview, entering `13800138000` routes to password login, not registration.
- Logging in with `13800138000 / Easewise123!` succeeds.
- The H5 app can show points, histories, and almanac data from mock APIs.
