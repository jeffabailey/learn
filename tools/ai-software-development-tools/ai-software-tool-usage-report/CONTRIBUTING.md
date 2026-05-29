# Contributing to ai-software-tool-usage-report

Thanks for considering a contribution. This guide covers how to get a working development environment, the conventions the code follows, and how to submit changes. It is structured per the InnerSource Commons [Base Documentation pattern][base-doc-pattern].

The tool lives in the [jeffabailey/learn][repo] monorepo at `tools/ai-software-development-tools/ai-software-tool-usage-report/`. Treat that subdirectory as the working root for everything in this guide.

## Source code checkout

```bash
git clone git@github.com:jeffabailey/learn.git
cd learn/tools/ai-software-development-tools/ai-software-tool-usage-report
```

## Development environment

Install Python 3.11 or newer, then install [uv][uv-install]:

```bash
brew install uv  # macOS
# or follow https://docs.astral.sh/uv/getting-started/installation/
```

Create the virtual environment and install runtime + dev dependencies:

```bash
uv sync --group dev
```

This creates `.venv/` and installs `httpx`, `python-dotenv`, `boto3`, `google-auth`, `requests`, and `pytest`.

Copy the env template and fill in credentials for any vendors to test against:

```bash
cp .env.example .env
```

The README's "Get the credentials" section documents what each vendor needs.

## Project layout

```text
ai-software-tool-usage-report/
  index.py             # CLI entry point
  pyproject.toml       # uv-managed deps and project metadata
  .env.example         # template for credentials
  vendors/
    base.py            # VendorAdapter + VendorReport dataclass
    anthropic.py
    openai_admin.py
    github_copilot.py
    cursor.py
    gemini.py
    aws_kiro.py
  tests/
    conftest.py        # shared fixtures
    test_index.py      # CLI / orchestration tests
    test_<vendor>.py   # one test module per adapter
```

## Coding guidelines

Follow these conventions to keep PRs reviewable:

* Target Python 3.11. Use `from __future__ import annotations` and modern type hints (`list[str]`, `dict[str, int]`, `X | None`).
* Match the existing module style: small functions, a top-level docstring on each new file, narrow exception handling.
* Keep adapters under `vendors/` self-contained. The contract is the `VendorAdapter` base class in `vendors/base.py`.
* Each adapter must carry a comment block at the top with the vendor doc URL and the response field path it sums. Vendor APIs drift; the comment is what makes the next fix a one-line change.
* Never log or commit credentials. The `.env` file is gitignored; keep it that way.

## Adding a new vendor adapter

1. Create `vendors/<vendor>.py`.
2. Subclass `VendorAdapter`. Implement `fetch(env, period_start, period_end) -> VendorReport`.
3. Read credentials from the env dict. Return `VendorReport.skipped(...)` when required env vars are missing or empty.
4. Register the new adapter in `vendors/__init__.py` (append to `ADAPTERS`).
5. Document the vendor's credential setup in `README.md` under "Get the credentials".
6. Add a `tests/test_<vendor>.py` mirroring `tests/test_anthropic.py`.

Errors raised inside `fetch` get caught at the top level and recorded as `SKIPPED` rows so a single broken vendor never aborts the run. Honor that contract.

## Build and run

There is no build step. Run the tool directly:

```bash
uv run python index.py                  # current month
uv run python index.py --month 2026-04  # a specific calendar month
uv run python index.py --output ./out   # custom output directory
uv run python index.py --help           # full CLI help
```

## Testing

Run the full suite before opening a PR:

```bash
uv run pytest
```

Conventions for test code:

* One test module per adapter (`test_<vendor>.py`), plus `test_index.py` for CLI / orchestration.
* Mock vendor HTTP calls. Tests must not make live network requests.
* Cover every new adapter and every behavior change. The CSV schema and the `SKIPPED` contract are both load-bearing; do not regress them.

If a change touches the CSV column order or names, update both `index.py` (`CSV_FIELDS`) and the README's "CSV columns" section in the same commit.

## Submitting changes

1. Branch from `main`: `git checkout -b feature/<short-name>` or `fix/<short-name>`.
2. Commit in small, focused units. Use conventional-commit prefixes where possible (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
3. Run `uv run pytest` and confirm a clean pass.
4. Push the branch and open a pull request against `main` of [jeffabailey/learn][repo].
5. In the PR description, explain the why, list manual test steps if any are needed, and link any related issue.

## Review turnaround

This is a personal learning repo, not a staffed project. There is no formal SLA. Expect a first response within a week for most PRs; trivial fixes (typos, docs) usually merge same-day. If a PR has been open more than two weeks without a response, comment on it to bump it.

## Reporting bugs

File an issue on [jeffabailey/learn][repo-issues]. Include:

* The command that was run.
* The full stderr output.
* Python and `uv` versions (`python --version`, `uv --version`).
* Vendor and approximate scale (seats, monthly cost ballpark) only when relevant. Never paste credentials.

## Code of conduct

Be kind. Assume good intent. Disagree about code, not about people.

[repo]: https://github.com/jeffabailey/learn
[repo-issues]: https://github.com/jeffabailey/learn/issues
[uv-install]: https://docs.astral.sh/uv/getting-started/installation/
[base-doc-pattern]: https://patterns.innersourcecommons.org/p/base-documentation
