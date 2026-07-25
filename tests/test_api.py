from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.models import ValidationResult, ValidationSummary


class FakeRunner:
    def validate(self, path: Path) -> ValidationResult:
        return ValidationResult(
            status="non_compliant",
            profile="PDF/UA-1",
            duration_ms=25,
            summary=ValidationSummary(passed_rules=10, failed_rules=1, passed_checks=20, failed_checks=2),
            issues=[],
        )

    def is_available(self) -> bool:
        return True


def test_index_is_accessible_and_explains_scope(tmp_path):
    app = create_app(settings=Settings(temp_dir=tmp_path), runner=FakeRunner())
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "PDF Accessibility Checker" in response.text
    assert "koneellisesti tarkistettavat" in response.text
    assert 'type="file"' in response.text


def test_validate_endpoint_returns_normalized_result(tmp_path):
    app = create_app(settings=Settings(temp_dir=tmp_path), runner=FakeRunner())
    client = TestClient(app)
    response = client.post("/api/validate", files={"file": ("sample.pdf", b"%PDF-1.7\nbody", "application/pdf")})
    assert response.status_code == 200
    assert response.json()["status"] == "non_compliant"
    assert response.json()["profile"] == "PDF/UA-1"


def test_validate_endpoint_rejects_invalid_file(tmp_path):
    app = create_app(settings=Settings(temp_dir=tmp_path), runner=FakeRunner())
    client = TestClient(app)
    response = client.post("/api/validate", files={"file": ("fake.pdf", b"hello", "application/pdf")})
    assert response.status_code == 400
    assert response.json()["detail"] == "Tiedosto ei ole kelvollinen PDF."


def test_health_reports_runner_readiness(tmp_path):
    app = create_app(settings=Settings(temp_dir=tmp_path), runner=FakeRunner())
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "verapdf": "available"}
