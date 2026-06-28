# AI Studio Sync Request

## Objective

I am starting from a new AI Studio account, and AI Studio cannot accept zip uploads. I will provide a large Markdown source bundle that expands every text file from the latest EaseWise source package.

Please treat the Markdown Bundle as the only source of truth and rebuild the EaseWise Vue 3 + Vite H5 prototype from it as completely and faithfully as possible.

The goal of this cycle is **not** to redesign freely. The goal is to restore the current project state inside AI Studio so future design iterations can continue from the real product UI.

## Uploaded Source Bundle

I will provide a Markdown file named similar to:

`EaseWise AI Studio Markdown Source Bundle`

It contains:

- reconstruction rules
- file tree
- one section per source file
- fenced code blocks containing each file's full content

Please inspect the bundle first, then recreate the project using the same architecture:

- Vue 3
- Vite
- TypeScript
- Tailwind-style utility classes / current CSS tokens
- Existing component structure under `src/components`
- Existing app navigation and tab flow
- Existing mock/server-compatible behavior in the uploaded package

Do not convert the project to React, Next.js, plain HTML, or a different architecture.

## Source Hierarchy

- The Markdown Bundle is authoritative for the current frontend source code, file structure, visual design, routes, components, and interaction states.
- Local product behavior from the source is authoritative for routes, API fields, auth, validation, state, points, payments, persistence, and business rules.
- AI Studio should be used as an editable design/prototype environment, not as a place to invent new backend contracts.
- If anything is unclear, preserve the uploaded source behavior and only make the smallest compatibility adjustment needed for AI Studio to run.

## Reconstruction Steps

1. Read the Markdown Bundle.
2. Recreate the file tree exactly from the `## File Tree` section.
3. For each `### \`path\`` section, create that file and copy the fenced code block content into it.
4. Preserve filenames, extensions, imports, component paths, and relative paths exactly.
5. Install/use the dependencies from `package.json`.
6. Run the Vite/Vue project in AI Studio preview.
7. If AI Studio requires a compatibility edit, keep it minimal and report the exact file and reason.

## Current Product Scope To Recreate

Please restore the full H5 prototype, including these major areas:

- Home page with current feature-card layout and animated entry icons.
- 奇门手机号评测 input flow, waiting state, result view, points handling, and insufficient-points state.
- 四柱八字评测 input flow, waiting state, natal chart result, aspect unlocks, luck-cycle / flowing-year views, and more-info modal.
- The latest 四柱八字 input page must be preserved very closely:
  - centered page header with title/subtitle and refresh affordance
  - compact title card with points badge
  - white form card
  - name input
  - side-by-side gender and calendar segmented controls
  - birth datetime summary row
  - birth location summary row
  - card-contained CTA button
  - date bottom sheet with `公历 / 农历` tabs, confirm button, manual numeric fields, and five-column wheel picker
  - location bottom sheet with `国内地区 / 海外地区`, search, wheel picker, and current location details
  - wheel columns should not show browser scrollbars
  - the design language should stay in the current EaseWise indigo / blue-gray / paper-white system; do not introduce black-gold or unrelated gold accents
- 梅花易数 frontend prototype page and home entry should be included as in the uploaded source.
- 智能体 page and bottom navigation spacing should match the uploaded source.
- 个人中心, 充值, 积分, auth modal, customer-service modal, and other supporting states should be retained.

## Critical Implementation Rules

1. Preserve Vue/Vite project structure.
2. Preserve `src/App.vue`, `src/main.ts`, `src/index.css`, `src/lib/api.ts`, `src/types/api.ts`, `src/composables/useEaseWiseApp.ts`, and all referenced components from the uploaded source.
3. Preserve existing route/tab names such as `home`, `phone`, `bazi`, `meihua`, `agent`, `profile`, `recharge`, and points-related pages.
4. Preserve pricing and points copy from the uploaded source.
5. Preserve loading, empty, error, disabled, insufficient-points, guest/login, and success states.
6. Do not remove backend-shaped API clients or type fields just because AI Studio is running as a prototype.
7. Do not replace real-looking product state with decorative placeholder content.
8. Do not simplify the Four Pillars input page back to an older form layout.
9. Do not import unrelated fantasy wording; use the current plain product terminology from the source.
10. Do not show visible browser scrollbars inside picker wheels.
11. If the bundle contains a `scrollbar-none` class but no matching CSS rule, add the same hiding rule used by `no-scrollbar`:
    - `::-webkit-scrollbar { display: none; }`
    - `scrollbar-width: none`
    - `-ms-overflow-style: none`

## Mock Data And Runtime Expectations

If AI Studio needs local mock data to render the prototype:

- Keep mock data compatible with the uploaded API/type shapes.
- Include enough points for a high-points full-regression account so every paid state can be viewed.
- Include low-points accounts or states for insufficient-points overlays.
- Include realistic Four Pillars natal chart data, aspect data, luck-cycle / flowing-year data, shen-sha rows, xun-kong rows, and more-info modal data.
- Include phone review data sufficient to view the full result page.
- Include empty-state and guest-state examples.

Do not invent new API field names when a field already exists in the uploaded `src/types/api.ts`.

## Visual Acceptance Checklist

After rebuilding, please verify the following in AI Studio preview:

- The project starts without TypeScript or Vite errors.
- The first screen is the actual EaseWise H5 app, not a landing-page placeholder.
- Bottom navigation appears and all main tabs/pages can be reached.
- Home page includes the current entries, including 四柱八字 and 梅花易数.
- 四柱八字 input page matches the uploaded source structure closely, especially the compact card layout and bottom sheets.
- Date picker wheels scroll smoothly and have no visible side scrollbars.
- Birth-location picker can display domestic and overseas selector states.
- The Four Pillars waiting animation and result page still render.
- Phone review flow still renders.
- Profile/recharge/points related UI still renders.
- Mobile viewport layout is prioritized; desktop preview should still be usable but H5 mobile is the primary target.

## Do Not Change

- Do not convert the app to another framework.
- Do not replace Vue state/composables with a new state system.
- Do not rename existing routes, API fields, or component contracts.
- Do not remove auth/points/insufficient-points logic.
- Do not remove the Meihua prototype.
- Do not redesign the Four Pillars input page away from the uploaded source.
- Do not reintroduce black-gold/gold visual styling where the uploaded current source uses the EaseWise indigo/blue-gray system.

## Output Request

Please implement the uploaded source in AI Studio and then provide:

- a concise summary of what was restored
- any files you changed for AI Studio compatibility
- any known gaps versus the uploaded source
- confirmation that the app builds/runs in AI Studio preview
