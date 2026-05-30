# Career Output Contract

## Required Fields

- `aspect_key`
- `title`
- `score`
- `content`
- `risk`
- `elements_check`

## Field Rules

`aspect_key` must be `career`.

`title` is one direct sentence about the career tendency.

`score` must use the locked score and cannot be changed.

`content` is one paragraph. It describes the career state, realistic manifestations, and mild usage advice.

`risk` is one paragraph. It focuses only on risks surfaced by `elements_check`, with a stronger warning tone than `content`.

`elements_check` must include `宫`, `门`, `神`, `星`, `天干/地干`, `特殊组合`, `四害`.

Do not output markdown or extra fields.
