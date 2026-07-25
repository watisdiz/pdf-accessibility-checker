from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import anyio
from fastapi import UploadFile

from app.config import Settings
from app.errors import InvalidPDFError, UploadTooLargeError
from app.models import ValidationResult
from app.runner import ValidationRunner

CHUNK_SIZE = 1024 * 1024
PDF_HEADER_SCAN_BYTES = 1024


async def validate_upload(
    upload: UploadFile,
    settings: Settings,
    runner: ValidationRunner,
) -> ValidationResult:
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = settings.temp_dir / f"{uuid4().hex}.pdf"
    total = 0
    header = bytearray()

    try:
        with temp_path.open("xb") as output:
            while chunk := await upload.read(CHUNK_SIZE):
                total += len(chunk)
                if total > settings.max_upload_bytes:
                    raise UploadTooLargeError("PDF ylittää sallitun kokorajan.")
                if len(header) < PDF_HEADER_SCAN_BYTES:
                    remaining = PDF_HEADER_SCAN_BYTES - len(header)
                    header.extend(chunk[:remaining])
                output.write(chunk)

        if not total or b"%PDF-" not in bytes(header):
            raise InvalidPDFError("Tiedosto ei ole kelvollinen PDF.")

        return await anyio.to_thread.run_sync(runner.validate, temp_path)
    finally:
        await upload.close()
        temp_path.unlink(missing_ok=True)
