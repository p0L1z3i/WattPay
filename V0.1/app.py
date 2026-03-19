#!/usr/bin/env python3
"""
WattPay FastAPI Application
This module defines the FastAPI application instance and registers all routers.
"""
import os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from api.owner.routes import router as owner_router

from api.common.config_manager import config
from api.common.log.logging import get_logger, set_file_handler_level

logger = get_logger(__name__)

# Enable or disable DEBUG-level file logging based on [logging] debug flag
if config.logging_config.debug:
    set_file_handler_level('DEBUG')
else:
    set_file_handler_level('INFO')


def _show_config_summary():
    """Fetch and display the application configuration summary."""
    logger.info("=" * 60)
    logger.info("WattPay - Configuration Summary")
    logger.info("=" * 60)
    logger.info("Full config summary: %s", config.get_config_summary())
    logger.info("=" * 60)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan event handler."""
    logger.info("WattPay application is starting up...")
    _show_config_summary()
    logger.info("WattPay application startup complete.")
    yield
    logger.info("WattPay application is shutting down...")
    logger.info("WattPay application shutdown complete.")


# ── FastAPI application setup ──────────────────────────────────
app = FastAPI(
    title="WattPay Unified API",
    version="0.0.1",
    description="WattPay - Electricity Consumption Tracking System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(owner_router, prefix="/owner", tags=["Owner"])


# Root Endpoint
@app.get("/")
async def root():
    """Root endpoint to verify application is running."""
    logger.debug("Root endpoint called")
    return {
        'message': (
            "Welcome to WattPay API! "
            "The application is running successfully."
        )
    }

if __name__ == "__main__":

    host = os.getenv("APP_SERVICE_HOST", "localhost")
    port = int(os.getenv("APP_SERVICE_PORT", "8000"))
    log_level = os.getenv("APP_LOGGING_LEVEL", "info").lower()

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level=log_level,
        access_log=True,
        reload=True
    )
