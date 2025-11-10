from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .metrics import add_metrics_middleware


def add_middlewares(app: FastAPI) -> None:
    _add_cors_middleware(app)
    add_metrics_middleware(app)


def _add_cors_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
