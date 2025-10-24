# Testing and CI/CD Documentation

This document describes the testing infrastructure and continuous integration setup for this repository.

## Overview

This repository uses GitHub Actions to automatically run tests and generate coverage reports for all projects on every push and pull request.

## Workflows

### 1. Test Coverage Workflow (`.github/workflows/test-coverage.yml`)

**Triggers:**
- Push to `main`, `master`, `develop`, or any `claude/*` branch
- Pull requests to `main`, `master`, or `develop`
- Manual workflow dispatch

**Jobs:**

#### Python Learning Content
- **Python Version:** 3.13
- **Dependencies:** Installed via pip with optional test dependencies
- **Tests:** pytest with coverage
- **Coverage:** Uploaded to Codecov with flag `python-learning`
- **Artifacts:** HTML coverage report (30 days retention)

#### Django HTMX Alpine (Python)
- **Python Version:** 3.10
- **Dependencies:** Installed via Poetry
- **Tests:** pytest-django with coverage
- **Coverage:** Uploaded to Codecov with flag `django-python`
- **Artifacts:** HTML coverage report (30 days retention)

#### Django HTMX Alpine (JavaScript)
- **Node.js Version:** 18
- **Dependencies:** Installed via npm
- **Tests:** Jest with coverage
- **Coverage Threshold:** 80% (branches, functions, lines, statements)
- **Coverage:** Uploaded to Codecov with flag `django-javascript`
- **Artifacts:** HTML coverage report (30 days retention)

#### LocalRAG ML Project
- **Python Version:** 3.10
- **System Dependencies:** tesseract-ocr, poppler-utils
- **Dependencies:** requirements.txt + pytest/pytest-cov
- **Tests:** pytest with coverage
- **Coverage:** Uploaded to Codecov with flag `localrag`
- **Artifacts:** HTML coverage report (30 days retention)

#### Coverage Summary
- **Depends on:** All test jobs
- **Purpose:** Aggregates results and displays summary
- **Outputs:** GitHub Step Summary with test status
- **Artifacts:** Downloads all coverage reports

### 2. Quick Tests Workflow (`.github/workflows/quick-test.yml`)

**Triggers:**
- Push to files in test directories
- Pull requests modifying test directories

**Purpose:** Fast feedback loop for developers

**Jobs:**

#### Quick Python Tests
- **Strategy:** Matrix build for multiple projects
- **Projects:** Python Learning, LocalRAG
- **Tests:** pytest without coverage (faster)
- **Failure:** Fails fast on first error

#### Quick JavaScript Tests
- **Tests:** Jest without coverage
- **Purpose:** Verify tests pass before full coverage run

#### Status Check
- **Purpose:** Combined status for all quick tests
- **Output:** Summary in GitHub Step Summary

## Coverage Configuration

### Codecov (`codecov.yml`)

**Settings:**
- **Precision:** 2 decimal places
- **Range:** 70-100%
- **Project Target:** Auto (maintain current coverage)
- **Patch Target:** 80%

**Flags:**
- `python-learning`: Python learning content
- `django-python`: Django Python code
- `django-javascript`: Django JavaScript code
- `localrag`: LocalRAG ML project

**Ignore Patterns:**
- Test files
- Migrations
- Node modules
- Configuration files

### Local Coverage

Each project has:
- **pytest.ini** or **package.json**: Test configuration
- **.coveragerc**: Coverage settings (Python projects)
- **Coverage reports**: Terminal, HTML, and LCOV

## Running Tests Locally

### Python Learning Content
```bash
cd programming/python
pytest --cov --cov-report=html
open htmlcov/index.html
```

### Django HTMX Alpine (Python)
```bash
cd frameworks/htmx/django-htmx-alpine
poetry install --with dev
poetry run pytest --cov --cov-report=html
open htmlcov/index.html
```

### Django HTMX Alpine (JavaScript)
```bash
cd frameworks/htmx/django-htmx-alpine
npm install
npm run jest-coverage
open coverage/index.html
```

### LocalRAG ML Project
```bash
cd machine-learning/localrag
pip install -r requirements.txt
pip install pytest pytest-cov
pytest --cov --cov-report=html
open htmlcov/index.html
```

## Viewing Coverage Reports

### On GitHub Actions

1. Go to the Actions tab
2. Select a workflow run
3. Scroll to Artifacts section
4. Download coverage report ZIP files
5. Extract and open `index.html`

### On Codecov

1. Visit [codecov.io/gh/jeffabailey/learn](https://codecov.io/gh/jeffabailey/learn)
2. View overall coverage and trends
3. Browse file-by-file coverage
4. View flag-specific coverage
5. Compare coverage between commits/branches

### Local Reports

HTML reports are generated in:
- `programming/python/htmlcov/`
- `frameworks/htmx/django-htmx-alpine/htmlcov/`
- `frameworks/htmx/django-htmx-alpine/coverage/`
- `machine-learning/localrag/htmlcov/`

## Coverage Badges

The README includes badges for:
- **Workflow Status:** Shows if tests are passing
- **Codecov:** Shows overall coverage percentage

Badges automatically update on each push.

## Pull Request Workflow

1. **Create PR** from feature branch
2. **Automatic Tests** run via GitHub Actions
3. **Coverage Report** generated and commented on PR
4. **Review Coverage** in Codecov PR comment
5. **Check Status** badges in PR checks
6. **Merge** when tests pass and coverage is acceptable

## Test Requirements for PRs

All pull requests should:
- ✅ Pass all tests in CI
- ✅ Maintain or improve coverage
- ✅ Meet JavaScript 80% threshold
- ✅ Include tests for new features
- ✅ Update tests for modified code

## Troubleshooting

### Tests fail locally but pass in CI
- Check Python/Node.js versions match CI
- Ensure all dependencies are installed
- Clear cache: `pip cache purge` or `npm cache clean --force`

### Coverage not uploading to Codecov
- Verify `CODECOV_TOKEN` secret is set in repository settings
- Check Codecov service status
- Review workflow logs for upload errors

### Coverage decreased unexpectedly
- Review Codecov diff to see uncovered lines
- Check if new code lacks tests
- Verify test exclusion patterns in `.coveragerc`

### Tests timeout in CI
- Check for infinite loops or blocking operations
- Add timeout limits to long-running tests
- Mock external dependencies

## Adding Tests to New Projects

To add test coverage to a new project:

1. **Create test files** following naming convention:
   - Python: `test_*.py` or `*_test.py`
   - JavaScript: `*.test.js` or `*.spec.js`

2. **Add test configuration:**
   - Python: Create `pytest.ini` and `.coveragerc`
   - JavaScript: Add Jest config to `package.json`

3. **Update workflows:**
   - Add new job to `test-coverage.yml`
   - Add to matrix in `quick-test.yml`

4. **Update documentation:**
   - Add to README test section
   - Add to `TEST_COVERAGE_SUMMARY.md`
   - Update `codecov.yml` with new flag

5. **Set coverage targets:**
   - Python: Configure in `.coveragerc`
   - JavaScript: Set threshold in `package.json`

## Best Practices

1. **Write tests first** (TDD) when adding features
2. **Run tests locally** before pushing
3. **Check coverage** locally before PR
4. **Add tests for bugs** to prevent regression
5. **Keep tests fast** for quick feedback
6. **Mock external dependencies** for reliability
7. **Use descriptive test names** for clarity
8. **Document complex test setups** with comments

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Jest documentation](https://jestjs.io/)
- [Codecov documentation](https://docs.codecov.com/)
- [GitHub Actions documentation](https://docs.github.com/actions)
- [Repository test summary](../TEST_COVERAGE_SUMMARY.md)

## Contact

For questions or issues with testing infrastructure, please open an issue or contact the repository maintainer.
