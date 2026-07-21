# Contributing to immoscout

Thanks for your interest in contributing! Bug reports, docs, new filters, and new
endpoints are all welcome.

## How to contribute

1. **Fork** the repository on GitHub.
2. **Clone** your fork: `git clone https://github.com/wiestju/ImmoScout.git`
3. **Create a branch:** `git checkout -b feature/my-change`
4. Make your changes with clear commit messages.
5. **Push** and **open a Pull Request**.

## Development setup

```bash
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"     # runtime + dev deps (pytest, ruff, responses)
```

## Before opening a PR

```bash
ruff check .     # lint (ruff check --fix . to auto-fix)
pytest           # unit tests are fully mocked — no network needed
```

Both run in CI on every push/PR across Python 3.10–3.13. Please keep them green and
add tests for new logic.

## Building the docs

```bash
pip install -e ".[docs]"
mkdocs serve     # live preview at http://127.0.0.1:8000
```

## Guidelines

- Ruff enforces style and imports (config in `pyproject.toml`); type-hint public APIs.
- Keep it **calm and respectful** of ImmobilienScout24 — timeouts, modest retries, no
  aggressive scraping. PRs that add mass-scraping or rate-limit evasion won't be merged.
  See [DISCLAIMER.md](DISCLAIMER.md).
- Never commit credentials, tokens, or personal data.

## Reporting issues

Open an issue with steps to reproduce, your Python version, and relevant output
(with any personal data redacted).
