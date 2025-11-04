#!/usr/bin/env python
"""Run the Holocratic ASGI application using uvicorn."""

from __future__ import annotations

import logging
from typing import Any

import uvicorn

from holocratic.api.main import create_app
from holocratic.config import get_settings


def configure_logging(level: str) -> None:
    """Configure application wide logging."""

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    """Entrypoint for serving the Holocratic API."""

    settings = get_settings()
    configure_logging(settings.log_level)

    uvicorn_kwargs: dict[str, Any] = {
        "host": settings.api_host,
        "port": settings.api_port,
        "log_level": settings.log_level,
        "factory": True,
        "reload": settings.reload,
        "workers": 1,
        "loop": "uvloop",
        "http": "h11",
    }

    uvicorn.run(create_app, **uvicorn_kwargs)


if __name__ == "__main__":  # pragma: no cover - script entry point
    main()
