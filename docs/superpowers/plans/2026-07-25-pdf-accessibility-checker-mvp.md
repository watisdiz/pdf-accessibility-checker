# PDF Accessibility Checker MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a private browser-based MVP that validates one PDF against veraPDF PDF/UA-1, displays normalized findings and deletes the upload after processing.

**Architecture:** A single FastAPI container owns upload handling, veraPDF process execution, report parsing and the web UI. Docker `tmpfs` provides non-persistent processing space, while an optional Cloudflare Tunnel container publishes the app behind Cloudflare Access.

**Tech Stack:** Python 3.13, FastAPI, Pydantic 2, Jinja2, vanilla JavaScript, veraPDF Greenfield 1.30.2, Docker Compose, Cloudflare Tunnel, pytest and GitHub Actions.

## Global Constraints

- Validate only with veraPDF `--flavour ua1`.
- Accept one PDF per request and reject application-level content above 20 MB.
- Use `/scan-tmp` for multipart spooling and validation files; do not create persistent upload storage.
- Run at most one validation process concurrently with a 60-second timeout.
- Never claim automated validation proves complete accessibility.
- Do not log original uploaded file names or PDF content.
- Initial public access is limited in Cloudflare Access to `timmy.lahteinen@gmail.com` by email OTP.

---

### Task 1: Stable validation result model and parser

**Files:**
- Create: `app/models.py`
- Create: `app/errors.py`
- Create: `app/parser.py`
- Test: `tests/test_parser.py`

**Interfaces:**
- Consumes: veraPDF machine-readable XML.
- Produces: `parse_verapdf_report(xml_text: str, duration_ms: int) -> ValidationResult`.

- [x] Write tests for compliant and non-compliant reports.
- [x] Run tests and confirm missing modules fail.
- [x] Implement Pydantic result models and robust report normalization.
- [x] Run parser tests and confirm passing tests.

### Task 2: Secure temporary upload lifecycle

**Files:**
- Create: `app/config.py`
- Create: `app/service.py`
- Test: `tests/test_service.py`

**Interfaces:**
- Consumes: FastAPI `UploadFile`, `Settings` and a `ValidationRunner`.
- Produces: `validate_upload(upload, settings, runner) -> ValidationResult`.

- [x] Write tests for a valid PDF, invalid signature, file-size rejection and cleanup.
- [x] Confirm tests fail before implementation.
- [x] Stream content to a UUID-named file, inspect the first 1024 bytes for `%PDF-`, enforce 20 MB and delete in `finally`.
- [x] Run service tests and confirm the temporary directory is empty after every path.

### Task 3: veraPDF process boundary

**Files:**
- Create: `app/runner.py`
- Modify: `app/config.py`
- Test: `tests/test_runner.py`

**Interfaces:**
- Produces: `VeraPDFRunner.validate(path: Path) -> ValidationResult` and `is_available() -> bool`.

- [x] Invoke `/opt/verapdf/verapdf` with an argument list, never through a shell.
- [x] Use `--flavour ua1`, `--format xml`, `--loglevel 0` and `--maxfailuresdisplayed 100`.
- [x] Convert timeouts, missing output and malformed XML into explicit checker errors.

### Task 4: HTTP API and accessible UI

**Files:**
- Create: `app/main.py`
- Create: `app/templates/index.html`
- Create: `app/static/styles.css`
- Create: `app/static/app.js`
- Test: `tests/test_api.py`

**Interfaces:**
- Produces: `GET /`, `POST /api/validate` and `GET /health`.

- [x] Test Finnish scope copy, normalized API output, invalid PDF response and readiness.
- [x] Implement a single concurrency semaphore and map expected errors to 400, 413, 422 and 504.
- [x] Build keyboard-accessible file selection, drag-and-drop enhancement, live status and structured results.
- [x] Generate the downloadable report from normalized client-side JSON so the server stores no result file.

### Task 5: Container and Cloudflare deployment

**Files:**
- Create: `Dockerfile`
- Create: `docker-install.xml`
- Create: `compose.yaml`
- Create: `.env.example`
- Create: `.dockerignore`
- Create: `.gitignore`

**Interfaces:**
- Produces: app on port 8080 and optional `cloudflared` profile.

- [x] Install stable veraPDF Greenfield 1.30.2 and OpenJDK 17 in the app image.
- [x] Run as UID 10001 with a read-only root filesystem and dropped capabilities.
- [x] Mount `/scan-tmp` as 128 MB `tmpfs`, cap memory at 1 GB and CPU at two cores.
- [x] Pin Cloudflare Tunnel image `2026.7.3` and accept its token only from `.env`.

### Task 6: Documentation and continuous verification

**Files:**
- Replace: `README.md`
- Create: `AGENTS.md`
- Create: `PROJECT_STATE.md`
- Create: `IDEAS_BACKLOG.md`
- Create: `docs/DECISIONS.md`
- Create: `docs/security.md`
- Create: `docs/operations.md`
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: reproducible local startup, Cloudflare setup checklist and CI checks.

- [x] Document local Docker start and the exact initial Access email policy.
- [x] Record architecture decisions and residual security limitations.
- [x] Run tests and Python bytecode compilation in CI.
- [x] Build the production Docker image in CI.
