from fastapi import FastAPI

from app.api.routes import (
    executions,
    health,
    problems,
    scenarios,
)

from app.core.config import get_settings

from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()


app = FastAPI(

    title=settings.app_name,

    version="0.1.0",

    description=(
        "Sistema computacional para modelagem "
        "e resolução de problemas de "
        "Programação Linear."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health.router,
    prefix=settings.api_prefix,
)

app.include_router(
    executions.router,
    prefix=settings.api_prefix,
)

app.include_router(
    problems.router,
    prefix=settings.api_prefix,
)

app.include_router(
    scenarios.router,
    prefix=settings.api_prefix,
)
from app.api.routes import resource_analysis

app.include_router(resource_analysis.router, prefix=settings.api_prefix)

from app.api.routes import resource_comparison

app.include_router(resource_comparison.router, prefix=settings.api_prefix)

from app.api.routes import management
app.include_router(management.router, prefix=settings.api_prefix)

