from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Protocol

from app.config import Settings
from app.errors import ValidationTimeoutError, VeraPDFExecutionError
from app.models import ValidationResult
from app.parser import parse_verapdf_report


class ValidationRunner(Protocol):
    def validate(self, path: Path) -> ValidationResult: ...

    def is_available(self) -> bool: ...


class VeraPDFRunner:
    def __init__(self, settings: Settings):
        self.settings = settings

    def is_available(self) -> bool:
        return self.settings.verapdf_path.is_file()

    def validate(self, path: Path) -> ValidationResult:
        started = time.monotonic()
        command = [
            str(self.settings.verapdf_path),
            "--flavour",
            "ua1",
            "--format",
            "xml",
            "--loglevel",
            "0",
            "--maxfailuresdisplayed",
            "100",
            str(path),
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.settings.validation_timeout_seconds,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValidationTimeoutError("PDF:n tarkistus ylitti aikarajan.") from exc
        except OSError as exc:
            raise VeraPDFExecutionError("veraPDF-tarkistusta ei voitu käynnistää.") from exc

        duration_ms = int((time.monotonic() - started) * 1000)
        if not completed.stdout.strip():
            raise VeraPDFExecutionError("veraPDF ei palauttanut luettavaa raporttia.")
        if completed.returncode not in (0, 1):
            raise VeraPDFExecutionError("veraPDF ei pystynyt käsittelemään PDF-tiedostoa.")

        return parse_verapdf_report(completed.stdout, duration_ms=duration_ms)
