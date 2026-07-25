# Operations

## Start locally

```bash
docker compose up -d --build
```

## Start with Cloudflare Tunnel

```bash
cp .env.example .env
# Add CLOUDFLARE_TUNNEL_TOKEN to .env
docker compose --profile cloudflare up -d --build
```

## Health and logs

```bash
curl http://localhost:8080/health
docker compose ps
docker compose logs app
docker compose logs cloudflared
```

Successful readiness response:

```json
{"status":"ok","verapdf":"available"}
```

## Upgrade

1. Review veraPDF and cloudflared release notes.
2. Update pinned versions in `Dockerfile` and `compose.yaml`.
3. Run unit tests and build the Docker image.
4. Validate known pass/fail fixtures manually.
5. Deploy and verify `/health` and an end-to-end upload.

## Incident response

- Stop services with `docker compose down`.
- Rotate the Cloudflare tunnel token if exposure is suspected.
- Review Cloudflare Access audit logs for authentication events.
- Do not expect historical PDF evidence from the app because uploads are not retained.
