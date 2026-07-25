# Project state

## Current

MVP implementation exists on branch `codex/mvp-verapdf-checker` with:

- FastAPI web application
- explicit veraPDF PDF/UA-1 validation
- normalized result model
- accessible Finnish upload and result interface
- RAM-backed temporary processing in Docker
- optional Cloudflare Tunnel service
- automated tests and GitHub Actions CI

## Next

1. Review and merge the draft pull request.
2. Build and run the Docker image locally.
3. Configure Cloudflare Access for `timmy.lahteinen@gmail.com`.
4. Create the tunnel route for `pdf.watisdis.com` to `http://app:8080`.
5. Test with known compliant, non-compliant, encrypted and malformed PDFs.

## Known limitation

FastAPI/Starlette parses multipart uploads before endpoint-level validation. The container therefore directs temporary multipart spooling to RAM-backed `/scan-tmp` and limits container memory, but the exact 20 MB rejection happens in the application service after multipart parsing.
