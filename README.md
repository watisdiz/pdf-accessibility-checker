# PDF Accessibility Checker

A small self-hosted web application that checks the machine-verifiable PDF/UA-1 requirements of one uploaded PDF using veraPDF.

## What the MVP does

- accepts one PDF at a time
- limits the application-level upload size to 20 MB
- validates explicitly against the veraPDF `ua1` profile
- shows a simple Finnish summary and failed rules
- lets the user download the normalized JSON result
- processes files in a RAM-backed Docker `tmpfs`
- removes each temporary PDF after success or failure
- supports optional Cloudflare Tunnel and Access protection

Passing veraPDF does not prove complete accessibility. Human checks such as the quality of alternative text, meaningful reading order and content clarity are still required.

## Local start

Requirements: Docker Desktop with Docker Compose.

```bash
docker compose build
docker compose up -d
```

Open `http://localhost:8080`.

Stop the application:

```bash
docker compose down
```

## Cloudflare-protected start

1. Create a Cloudflare Access self-hosted application for `pdf.watisdis.com`.
2. Create an Allow policy for the exact email `timmy.lahteinen@gmail.com`.
3. Enable email one-time PIN login.
4. Create a Cloudflare Tunnel and set its service URL to `http://app:8080`.
5. Copy `.env.example` to `.env` and add the tunnel token.
6. Start the application and tunnel:

```bash
docker compose --profile cloudflare up -d --build
```

Create the Access application before publishing the tunnel route. This prevents an unprotected public interval during setup.

## Development

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
uvicorn app.main:app --reload --port 8080
```

A local development run without veraPDF installed will return `503` from `/health`, but the UI and unit tests can still be developed using injected test runners.

## Endpoints

- `GET /` web interface
- `POST /api/validate` multipart PDF validation
- `GET /health` application and veraPDF readiness

## Security and privacy

The application does not use a database or persistent upload volume. The Docker service runs as an unprivileged user, drops Linux capabilities, uses a read-only root filesystem and stores temporary data under `/scan-tmp` mounted as `tmpfs`. Application access logs are disabled so uploaded file names are not written by Uvicorn.

See `docs/security.md` and `docs/operations.md` for the deployment checklist and limitations.
