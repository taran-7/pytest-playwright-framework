# pytest-playwright-framework

[![Test Docker Compose](../../actions/workflows/test-docker-compose.yml/badge.svg)](../../actions/workflows/test-docker-compose.yml)
[![Test Backend](../../actions/workflows/test-backend.yml/badge.svg)](../../actions/workflows/test-backend.yml)
[![Test QA](../../actions/workflows/test-qa.yml/badge.svg)](../../actions/workflows/test-qa.yml)

A training playground for test automation with Python and Playwright. A real web application is tested in layers (unit, component, API, UI, accessibility and performance), and each layer is a quality gate in CI.

The application under test is a one-time import of [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) (FastAPI, PostgreSQL, React). It is not kept in sync with upstream and may be changed freely to make it easier to test.

## Repository layout

| Path | What it is |
|---|---|
| `backend/`, `frontend/` | The system under test (SUT). It has stable `data-testid` attributes and a repeatable test data seeder. |
| `qa/` | The test project: Python 3.15, uv, pytest and Playwright. It talks to the SUT only over HTTP and is configured with environment variables. |
| `.github/` | CI workflows and the Renovate configuration. |

## Quick start

You need [Docker](https://docs.docker.com/get-docker/) and [uv](https://docs.astral.sh/uv/). uv downloads Python 3.15 by itself.

Start the SUT with the seeded test users on <http://localhost:8000>:

```bash
docker compose run --rm backend bash scripts/prestart.sh
docker compose run --rm backend python app/seed_test_data.py
docker compose up -d --wait backend
```

Install the browser once, then run the tests with one command:

```bash
cd qa
uv run playwright install chromium
uv run pytest
```

Stop the SUT with `docker compose down`, or `docker compose down -v` to also drop its database.

## Configuration

The tests are configured with environment variables. For local runs they can also be put in `qa/.env`, see `qa/.env.example`.

| Variable | Default | Meaning |
|---|---|---|
| `QA_ENV` | `local` | Where the tests run: `local` or `ci`. |
| `QA_BASE_URL` | `http://localhost:8000` | Origin of the SUT. The frontend and the API share it. |

## Quality checks

The `qa/` project is checked with Ruff (all rules), mypy in strict mode and pytest in strict mode (unknown markers and unexpected passes of `xfail` tests fail the run):

```bash
cd qa
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

The same checks run as pre-commit hooks. Install them once from the repository root with `uv run prek install -f`, see [development.md](./development.md#pre-commit-hooks-and-code-linting).

## Continuous integration

| Workflow | Runs on | What it checks |
|---|---|---|
| pre-commit | every pull request | The hooks for the SUT and for `qa/`. |
| Test Backend | every pull request | The backend test suite. |
| Test Docker Compose | every pull request | The stack builds, migrates, seeds and answers requests. |
| Test QA | changes under `qa/` | Ruff, mypy and the self tests of `qa/`, including a Chromium run. |
| Zizmor | every pull request | Security audit of the workflows. |

The `master` branch is protected by a ruleset: changes go through a pull request, and the checks `pre-commit-alls-green`, `test-backend`, `test-docker-compose` and `Run zizmor` must pass.

## More documentation

- [development.md](./development.md): running and developing the SUT, including the test data seeder.
- [backend/README.md](./backend/README.md) and [frontend/README.md](./frontend/README.md): the SUT parts.
- [CONTRIBUTING.md](./CONTRIBUTING.md): how to propose changes.
- [SECURITY.md](./SECURITY.md): how to report a vulnerability.

## License

MIT, see [LICENSE](./LICENSE).
