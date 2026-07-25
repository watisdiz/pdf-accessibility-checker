from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    max_upload_bytes: int = 20 * 1024 * 1024
    temp_dir: Path = Path("/scan-tmp")
    validation_timeout_seconds: int = 60
    max_concurrent_scans: int = 1
    verapdf_path: Path = Path("/opt/verapdf/verapdf")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", str(20 * 1024 * 1024))),
            temp_dir=Path(os.getenv("SCAN_TEMP_DIR", "/scan-tmp")),
            validation_timeout_seconds=int(os.getenv("VALIDATION_TIMEOUT_SECONDS", "60")),
            max_concurrent_scans=int(os.getenv("MAX_CONCURRENT_SCANS", "1")),
            verapdf_path=Path(os.getenv("VERAPDF_PATH", "/opt/verapdf/verapdf")),
        )
