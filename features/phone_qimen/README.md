# Phone Qimen

This feature owns the digital Qimen phone-number review capability.

The active implementation now lives here:

- `knowledge/`: phone summary, phone-specific stability judgement, shared interpretation boundaries, and aspect packs.
- `scoring/`: deterministic total score, board facts, dimensions, and phone stability scoring.
- `rendering/`: phone summary, phone stability detail, and aspect LLM rendering.

The public API contract is `/api/v1/phone-qimen/*`.
