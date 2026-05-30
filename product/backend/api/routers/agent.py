from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

router.add_api_route("/reply", handlers.create_agent_reply, methods=["POST"], response_model=handlers.AgentReplyResponse)
