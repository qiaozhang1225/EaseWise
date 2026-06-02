from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])

router.add_api_route("/narrations", handlers.create_voice_narration, methods=["POST"], response_model=handlers.VoiceNarrationResponse)
