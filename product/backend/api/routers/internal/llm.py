from __future__ import annotations

from fastapi import APIRouter

from product.backend.api import handlers

router = APIRouter(prefix="/api/v1/internal/llm", tags=["internal-llm"])

router.add_api_route("/concurrency", handlers.get_internal_llm_concurrency, methods=["GET"], response_model=handlers.LlmConcurrencyStatusResponse)
router.add_api_route("/api-keys", handlers.get_internal_llm_api_keys, methods=["GET"], response_model=handlers.LlmApiKeyListResponse)
router.add_api_route("/api-keys", handlers.post_internal_llm_api_key, methods=["POST"], response_model=handlers.LlmApiKeyResponse)
router.add_api_route("/api-keys/{key_id}", handlers.patch_internal_llm_api_key, methods=["PATCH"], response_model=handlers.LlmApiKeyResponse)
router.add_api_route("/api-keys/{key_id}", handlers.delete_internal_llm_api_key, methods=["DELETE"], include_in_schema=False)
