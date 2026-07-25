# Architecture decisions

## ADR-001: Single application container

The FastAPI application and veraPDF CLI are installed in the same image. This avoids file transfer between services and is adequate for a single-user MVP.

## ADR-002: PDF/UA-1 only

The application always invokes veraPDF with `--flavour ua1`. Automatic profile detection and PDF/UA-2 are outside the MVP.

## ADR-003: No persistent storage

Uploaded files and multipart spooling use `/scan-tmp`, mounted as Docker `tmpfs`. No database, object store or Docker volume stores PDFs or results.

## ADR-004: Cloudflare Access outside application code

Authentication is configured in Cloudflare Access, initially allowing only `timmy.lahteinen@gmail.com` with a one-time PIN. The email address and policy are not application runtime secrets.

## ADR-005: Normalized result model

The browser receives a stable application-owned JSON model instead of the raw veraPDF schema. This isolates the UI from report-format changes and avoids exposing local temporary file paths.

## ADR-006: No invented severity levels

veraPDF rules are shown as failed rules and occurrences. The MVP does not invent critical, high, medium or low classifications.
