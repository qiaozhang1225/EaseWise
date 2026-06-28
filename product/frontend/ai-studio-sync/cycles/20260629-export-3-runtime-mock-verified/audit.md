# AI Studio Export 3 Runtime Mock Audit

## Source

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise (3).zip`
- SHA256: `bab6b0b79d887c10d3b8b5c2060a7c2325da79c411788b81fbad53d27d2ee618`
- Clean extraction: `/tmp/easewise-export-3-clean`
- File count: `39`

## Verification Summary

AI Studio's latest written summary is mostly confirmed by the exported code.

## Confirmed Fixes

### 1. Custom mock server is wired into development

`package.json` now contains:

```json
"dev": "tsx server.ts",
"dev:vite": "vite --port=3000 --host=0.0.0.0"
```

and `tsx` is present in `devDependencies`.

This means `npm run dev` now starts the Express custom server, which mounts Vite middleware and serves mock `/api/v1/...` routes from the same origin.

### 2. Environment guidance is corrected

`.env.example` now says:

```text
# Leave empty or set to / during local development so requests are routed to the same origin.
# DO NOT set VITE_API_BASE_URL to /api for this project, as paths already include /api/v1.
VITE_API_BASE_URL=/
VITE_APP_BASE_PATH=/
```

This avoids the previous `/api/api/v1/...` path issue.

### 3. Phone status response matches frontend contract

`server.ts` now returns:

```ts
res.json({
  registered: isRegistered,
  normalized_phone: normalizedPhone,
  next_action: isRegistered ? "login" : "register",
});
```

This matches `PhoneStatusResponse` and `AuthModal.vue`.

### 4. Lint and build pass

After dependency install in a temporary verification directory:

```text
npm run lint  -> passed
npm run build -> passed
```

### 5. Mock endpoints verified

Because local port `3000` was already occupied by the local EaseWise service, verification temporarily changed the extracted copy's port to `3303` only in `/tmp` and started `server.ts`.

Verified:

- `POST /api/v1/auth/phone/status`
  - `13800138000` -> `registered: true`
  - `13600136000` -> `registered: true`
  - `13500135000` -> `registered: true`
  - `13900139000` -> `registered: true`
  - `13700137000` -> `registered: true`
  - unknown valid phone -> `registered: false`
- `POST /api/v1/auth/phone/login`
  - `13800138000 / Easewise123!` returns access token and points.
- `GET /api/v1/almanac/today`
  - returns almanac JSON.

## Remaining Notes

### Port is still hardcoded

`server.ts` still contains:

```ts
const PORT = 3000;
```

This is acceptable for AI Studio single-project preview, but inconvenient for local parallel verification. A future optional improvement would be:

```ts
const PORT = Number(process.env.PORT || 3000);
```

### README is generic

The README still uses the generic AI Studio starter wording and does not explain the mock server / env settings. `.env.example` is correct, so this is not blocking.

## Recommendation

This export has fixed the previous runtime/mock wiring problem. The next AI Studio interaction can move back to design/product iteration instead of runtime plumbing, unless the user sees a new preview-only issue.
