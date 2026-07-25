import subprocess
from pathlib import Path

import pytest

from app.config import Settings
from app.errors import ValidationTimeoutError
from app.runner import VeraPDFRunner


def test_runner_uses_explicit_ua1_xml_command(monkeypatch, tmp_path):
    pdf = tmp_path / "opaque-id.pdf"
    pdf.write_bytes(b"%PDF-1.7")
    settings = Settings(verapdf_path=Path("/opt/verapdf/verapdf"), temp_dir=tmp_path)
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            command,
            returncode=0,
            stdout='''<report><jobs><job><validationReport profileName="PDF/UA-1 validation profile" isCompliant="true"><details passedRules="1" failedRules="0" passedChecks="1" failedChecks="0" /></validationReport></job></jobs></report>''',
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = VeraPDFRunner(settings).validate(pdf)

    assert result.status == "compliant"
    assert captured["command"] == [
        "/opt/verapdf/verapdf", "--flavour", "ua1", "--format", "xml",
        "--loglevel", "0", "--maxfailuresdisplayed", "100", str(pdf),
    ]
    assert captured["kwargs"]["shell"] is False


def test_runner_converts_timeout(monkeypatch, tmp_path):
    pdf = tmp_path / "opaque-id.pdf"
    pdf.write_bytes(b"%PDF-1.7")
    settings = Settings(verapdf_path=Path("/opt/verapdf/verapdf"), temp_dir=tmp_path)

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=60)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(ValidationTimeoutError):
        VeraPDFRunner(settings).validate(pdf)
