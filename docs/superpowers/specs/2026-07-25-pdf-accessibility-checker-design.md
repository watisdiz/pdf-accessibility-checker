# PDF Accessibility Checker MVP Design

## Goal

Build a small self-hosted browser application that validates one uploaded PDF against veraPDF's machine-verifiable PDF/UA-1 rules and presents a clear Finnish result without storing the document.

## Users and access

The initial user is `timmy.lahteinen@gmail.com`. Authentication is handled by Cloudflare Access with an email one-time PIN. The application itself contains no user database or authentication logic.

## User flow

1. The user opens `pdf.watisdis.com` and authenticates through Cloudflare Access.
2. The user selects or drops one PDF of at most 20 MB.
3. The application saves the upload under a generated name in RAM-backed temporary storage.
4. veraPDF runs with the explicit `ua1` profile and machine-readable XML output.
5. The application normalizes the report and displays compliance, counts, failed rules and technical contexts.
6. The user may download the normalized JSON result.
7. The temporary PDF is deleted whether validation succeeds or fails.

## Architecture

The solution is one FastAPI application container containing Python, Java and veraPDF CLI. An optional `cloudflared` Compose service publishes the application through an outbound Cloudflare Tunnel. The app has no database, queue, persistent upload volume or analytics.

### Components

- `app/main.py`: HTTP routes, templates, error mapping and concurrency gate.
- `app/service.py`: upload streaming, size/signature checks, temporary file lifecycle.
- `app/runner.py`: shell-free veraPDF process invocation and timeout.
- `app/parser.py`: converts veraPDF XML into stable application models.
- `app/templates` and `app/static`: keyboard-usable upload and result interface.
- Docker Compose: resource limits, RAM-backed storage and optional tunnel.

## Data handling

Multipart spooling and validation files use `/scan-tmp`, mounted as a 128 MB `tmpfs`. The root filesystem is read-only and no persistent volume is defined. Original file names are not passed to veraPDF or written by application access logs.

## Validation behaviour

veraPDF version 1.30.2 is installed from the stable Greenfield installer. The command uses `--flavour ua1`, XML output, disabled console logging and a maximum of 100 displayed failures per rule. A process timeout of 60 seconds and one concurrent validation limit protect the host.

## Result semantics

The result may state that the PDF passed or failed veraPDF's machine-verifiable PDF/UA-1 checks. It must not claim that the PDF is fully accessible. The interface explains that alternative-text quality, meaningful reading order and understandable content can require human review.

## Error handling

- Invalid PDF signature: HTTP 400.
- File above 20 MB: HTTP 413.
- veraPDF report or processing failure: HTTP 422.
- validation timeout: HTTP 504.
- unavailable veraPDF binary: readiness endpoint returns HTTP 503.

All expected failures remove the temporary file.

## Testing

Automated tests cover report normalization, valid upload flow, size rejection, PDF signature rejection, cleanup, API responses and readiness. GitHub Actions runs tests, Python compilation and a Docker build.

## Out of scope

PDF/UA-2, PAC automation, AI remediation, batch files, scan history, external APIs, analytics, severity scoring and organisation-wide identity integration are not part of this MVP.
