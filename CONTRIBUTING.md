# Contributing

This is a training project for Python and Playwright test automation. Suggestions and pull requests are welcome. For a larger change, open an issue first so the approach can be discussed before you spend time on it.

## Setting up

Follow the quick start in the [README](./README.md) to run the application under test, and [development.md](./development.md) for working on it. Install the pre-commit hooks once from the repository root:

```bash
uv run prek install -f
```

## Making a change

1. Branch from `master`. Name the branch after the work, for example `phase-2/unit-tests`.
2. Keep one logical change per commit. Write commit messages in English, in the imperative mood ("Add seeder", not "Added seeder"), with a short subject and a body that explains why.
3. Open a pull request against `master`. Describe what changed, why, and how you verified it.
4. The `master` branch is protected: it accepts changes only through a pull request whose required checks are green (`pre-commit-alls-green`, `test-backend`, `test-docker-compose` and `Run zizmor`). Merge `master` into your branch if it moved on.

Keep pull requests focused. Work is planned in phases and each phase is its own pull request.

## Writing tests

The tests live in `qa/` and are checked by Ruff with all rules enabled, mypy in strict mode and pytest in strict mode.

- Locate elements with `page.get_by_test_id(...)`. The SUT exposes `data-testid` attributes in kebab-case with a type suffix, such as `add-item-button` or `item-title-input`. If an element has none, add one to the frontend instead of reaching for a CSS or XPath selector.
- Annotate every function. Mark a test with `smoke` or `regression` when it belongs to a suite.
- A test that is expected to fail uses `xfail` with a reason. Pytest runs in strict mode, so it fails the run once the bug is fixed and the marker is stale.
- Configuration comes from the environment through `framework.config.Settings`. Do not hardcode URLs or credentials in tests.

Run the checks locally before you push:

```bash
cd qa
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --cov
```

New code needs tests. CI fails when the backend coverage drops below 90% or when the coverage of `qa/framework` drops below 80%. How to run the backend tests with coverage is described in [backend/README.md](./backend/README.md).

## Dependencies

Dependency updates are proposed by Renovate once a month. Major updates wait for approval in the Dependency Dashboard issue. When you change `qa/pyproject.toml`, run `uv lock` in `qa/` and commit `uv.lock` too, because CI installs with `--locked`.

## Using AI tools

Use whatever tools you like, including AI assistants. You are responsible for what you submit: read it, run it, and be able to explain it.

## Security

Do not report vulnerabilities in a public issue. See [SECURITY.md](./SECURITY.md).
