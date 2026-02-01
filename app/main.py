from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import api_router


def create_application() -> FastAPI:
    app = FastAPI(
        title="Save Mo Finance API",
        version="0.1.0",
        description="Backend API for the Save Mo Finance platform.",
    )

    # Open CORS for now (allow all origins). Tighten this in production.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_application()

