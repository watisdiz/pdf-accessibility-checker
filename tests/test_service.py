from pathlib import Path

import pytest
from starlette.datastructures import UploadFile

from app.config import Settings
from app.errors import InvalidPDFError, UploadTooLargeError
from app.models import ValidationResult, ValidationSummary
from app.service import validate_upload


class RecordingRunner:
    def __init__(self):
        self.paths: list[Path] = []

    def validate(self, path: Path) -> ValidationResult:
        self.paths.append(path)
        assert path.exists()
        return ValidationResult(
            status="compliant",
            profile="PDF/UA-1",
            duration_ms=10,
            summary=ValidationSummary(passed_rules=1, failed_rules=0, passed_checks=1, failed_checks=0),
            issues=[],
        )

    def is_available(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_validate_upload_cleans_up_temporary_pdf(tmp_path):
    runner = RecordingRunner()
    settings = Settings(temp_dir=tmp_path, max_upload_bytes=1024)
    upload = UploadFile(filename="sample.pdf", file=__import__("io").BytesIO(b"%PDF-1.7\nbody"))

    result = await validate_upload(upload, settings, runner)

    assert result.status == "compliant"
    assert len(runner.paths) == 1
    assert not runner.paths[0].exists()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.asyncio
async def test_validate_upload_rejects_non_pdf_signature(tmp_path):
    settings = Settings(temp_dir=tmp_path, max_upload_bytes=1024)
    upload = UploadFile(filename="fake.pdf", file=__import__("io").BytesIO(b"not-a-pdf"))

    with pytest.raises(InvalidPDFError):
        await validate_upload(upload, settings, RecordingRunner())

    assert list(tmp_path.iterdir()) == []


@pytest.mark.asyncio
async def test_validate_upload_rejects_file_over_limit(tmp_path):
    settings = Settings(temp_dir=tmp_path, max_upload_bytes=8)
    upload = UploadFile(filename="large.pdf", file=__import__("io").BytesIO(b"%PDF-123456789"))

    with pytest.raises(UploadTooLargeError):
        await validate_upload(upload, settings, RecordingRunner())

    assert list(tmp_path.iterdir()) == []
