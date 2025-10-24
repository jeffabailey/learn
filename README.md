# Jeff Bailey's Blog

[![Test Coverage](https://github.com/jeffabailey/learn/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/jeffabailey/learn/actions/workflows/test-coverage.yml)
[![codecov](https://codecov.io/gh/jeffabailey/learn/branch/main/graph/badge.svg)](https://codecov.io/gh/jeffabailey/learn)

A technology blog by [Jeff Bailey](https://jeffbailey.us).

Repository contains companion learning materials with comprehensive test coverage.

Folders contain a README.md with link to blog post(s).

## Test Coverage

This repository includes comprehensive test coverage for all learning materials:

- **84+ tests** across Python, JavaScript, and ML projects
- **Automated testing** via GitHub Actions
- **Coverage reporting** with Codecov
- **80% coverage threshold** for JavaScript

See [TEST_COVERAGE_SUMMARY.md](TEST_COVERAGE_SUMMARY.md) for details.

### Running Tests Locally

```bash
# Python Learning Content
cd programming/python && pytest --cov

# Django HTMX Alpine (Python)
cd frameworks/htmx/django-htmx-alpine && pytest --cov

# Django HTMX Alpine (JavaScript)
cd frameworks/htmx/django-htmx-alpine && npm run jest-coverage

# LocalRAG ML Project
cd machine-learning/localrag && pytest --cov
```

# All Blog Post Categories

Automation
Books
Bugs
Culture
Data
DevOps
Hardware
Languages
Leadership
Music
Operating Systems
Professional Development
Programming
Security
Software
Tools
Users
