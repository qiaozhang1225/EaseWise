from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import handlers
from .routers import account, agent, almanac, auth, billing, phone_qimen, public, runtime_config
from .routers.internal import (
    almanac as internal_almanac,
    billing as internal_billing,
    dashboard as internal_dashboard,
    llm as internal_llm,
    platform as internal_platform,
    phone_qimen as internal_phone_qimen,
    promotion as internal_promotion,
    runtime_config as internal_runtime_config,
    users as internal_users,
)

app = FastAPI(title=handlers.APP_TITLE, version=handlers.APP_VERSION)
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=handlers.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    handlers.ensure_schema()


app.include_router(public.router)
app.include_router(auth.router)
app.include_router(account.router)
app.include_router(billing.router)
app.include_router(runtime_config.router)
app.include_router(agent.router)
app.include_router(almanac.router)
app.include_router(phone_qimen.router)
app.include_router(internal_dashboard.router)
app.include_router(internal_users.router)
app.include_router(internal_phone_qimen.router)
app.include_router(internal_almanac.router)
app.include_router(internal_platform.router)
app.include_router(internal_runtime_config.router)
app.include_router(internal_billing.router)
app.include_router(internal_llm.router)
app.include_router(internal_promotion.router)
app.mount("/api/v1/static", StaticFiles(directory=str(STATIC_DIR)), name="api_static")
