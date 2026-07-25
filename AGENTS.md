# Project instructions

- Keep the MVP focused on one-file PDF/UA-1 validation with veraPDF.
- Use test-driven development for behaviour changes.
- Do not add persistent storage, analytics, AI remediation, PAC automation or multi-file processing without an explicit scope decision.
- Never log uploaded PDF content or original file names.
- Keep veraPDF invocation shell-free and pass arguments as a list.
- Preserve the user-facing distinction between machine-verifiable PDF/UA-1 checks and complete accessibility.
- Keep the interface keyboard usable and screen-reader friendly.
- Update `PROJECT_STATE.md` and `docs/DECISIONS.md` when scope or architecture changes.
