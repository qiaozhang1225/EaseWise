# EaseWise Features

`features/` is the home for product capabilities that sit at the same product level.

- `phone_qimen/`: digital Qimen phone-number review.
- `four_pillars/`: Four Pillars / Ba Zi, currently prepared as a future feature.
- `almanac/`: almanac and daily calendar logic.

Product API routes live under `product/backend/api/routers/` and should call into these feature modules instead of adding feature logic directly to the API entrypoint.
