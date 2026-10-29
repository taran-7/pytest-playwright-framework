# Security Policy

## Scope

This is a training project. The application under test is a demo application that is started locally or in CI, and it is not meant to be deployed. The following is intentional and not a vulnerability:

- The `.env` file contains placeholder secrets (`changethis`) so that the stack starts without setup. Never reuse them anywhere that is reachable from outside your machine.
- With `FASTAPI_ENV=development` the backend exposes a private route that creates users, and `app/seed_test_data.py` creates users with a shared password. Both are available only in that environment.

Anything else is in scope, for example a way around the authentication or permission checks, a leaked secret, or a vulnerable dependency or workflow configuration.

## Supported versions

Only the current `master` branch is supported.

## Reporting a vulnerability

Do not open a public issue. Use the private report form: open the Security tab of the repository, choose "Report a vulnerability", and describe the problem, how to reproduce it, and its impact.

Reports are handled on a best-effort basis, and fixes are made on `master`.
