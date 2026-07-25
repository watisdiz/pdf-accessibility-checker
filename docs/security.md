# Security and privacy

## Controls included

- Cloudflare Access is the intended public authentication layer.
- The first policy allows only `timmy.lahteinen@gmail.com` using email OTP.
- The app container runs as UID/GID 10001.
- Root filesystem is read-only.
- Linux capabilities are dropped and `no-new-privileges` is enabled.
- Temporary files use a 128 MB `tmpfs` with `noexec`, `nosuid` and `nodev`.
- Application memory is limited to 1 GB and CPU to two cores.
- One validation runs at a time and each veraPDF process has a 60-second timeout.
- veraPDF is launched without a shell and with a generated UUID file name.
- Uvicorn access logging is disabled.
- Temporary files are removed in a `finally` block.

## Deployment checklist

1. Create the Access application before the public tunnel hostname.
2. Allow exactly `timmy.lahteinen@gmail.com`.
3. Enable one-time PIN identity provider.
4. Enable “Protect with Access” for the tunnel route when available.
5. Keep `.env` out of Git and rotate a disclosed tunnel token immediately.
6. Do not publish port 8080 on a non-loopback host interface.
7. Apply Docker and veraPDF security updates through reviewed pull requests.

## Residual risks

- A malicious but authenticated PDF may consume CPU or memory before timeout.
- Multipart parsing occurs before application-level size rejection, though spooling is directed to RAM-backed storage.
- Automated PDF/UA validation does not cover human accessibility checkpoints.
- The application has not yet undergone independent penetration or accessibility testing.
