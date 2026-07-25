from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import Settings
from app.errors import (
    InvalidPDFError,
    UploadTooLargeError,
    ValidationTimeoutError,
    VeraPDFExecutionError,
)
from app.models import ValidationResult
from app.runner import ValidationRunner, VeraPDFRunner
from app.service import validate_upload

BASE_DIR = Path(__file__).resolve().parent


def create_app(
    settings: Settings | None = None,
    runner: ValidationRunner | None = None,
) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    resolved_runner = runner or VeraPDFRunner(resolved_settings)
    semaphore = asyncio.Semaphore(resolved_settings.max_concurrent_scans)

    app = FastAPI(title="PDF Accessibility Checker", version="0.1.0")
    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
    templates = Jinja2Templates(directory=BASE_DIR / "templates")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "max_upload_mb": resolved_settings.max_upload_bytes // (1024 * 1024),
            },
        )

    @app.post("/api/validate", response_model=ValidationResult)
    async def validate(file: UploadFile = File(...)) -> ValidationResult:
        try:
            async with semaphore:
                return await validate_upload(file, resolved_settings, resolved_runner)
        except InvalidPDFError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except UploadTooLargeError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        except ValidationTimeoutError as exc:
            raise HTTPException(status_code=504, detail=str(exc)) from exc
        except VeraPDFExecutionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/health")
    async def health() -> JSONResponse:
        if resolved_runner.is_available():
            return JSONResponse({"status": "ok", "verapdf": "available"})
        return JSONResponse(
            {"status": "degraded", "verapdf": "unavailable"}, status_code=503
        )

    return app


app = create_app()
