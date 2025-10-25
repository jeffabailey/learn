# Learning Python

A companion repository for this blog post: <https://jeffbailey.us/blog/2020/05/26/learn-python/>

This folder contains beginner-friendly Python learning materials covering fundamental concepts. Each file is a standalone example that demonstrates a specific Python concept.

## What You'll Learn

- **Variables** (`variables.py`) - Learn about different data types: strings, integers, floats, and booleans
- **Operators** (`operators.py`) - Understand arithmetic and assignment operators
- **Arrays/Lists** (`arrays.py`) - Work with lists: accessing, modifying, and iterating
- **Control Structures** (`control_structures.py`) - Master for loops, while loops, and if-else statements
- **Functions** (`functions.py`) - Create and use functions with file operations
- **Classes and Objects** (`classes_and_objects.py`) - Introduction to object-oriented programming
- **Lambdas** (`lambdas.py`) - Use lambda functions for simple operations
- **Exception Handling** (`exception_handling.py`) - Handle errors gracefully with try-except blocks
- **Comments** (`comments.py`) - Learn proper commenting techniques

## Prerequisites

- **Python 3.10 or higher** - Check your version by running: `python --version` or `python3 --version`
- **pip** - Python package installer (usually comes with Python)

If you don't have Python installed, visit [python.org](https://www.python.org/downloads/) to download it.

## Setup Instructions

### Step 1: Clone or Download This Folder

You can clone just this folder using git sparse-checkout:

```bash
# Clone the repository with sparse checkout
git clone --depth 1 --filter=blob:none --sparse https://github.com/jeffabailey/learn
cd learn
git sparse-checkout set programming/python
cd programming/python
```

Or download the entire repository and navigate to this folder:

```bash
git clone https://github.com/jeffabailey/learn
cd learn/programming/python
```

### Step 2: Install Dependencies

This project uses minimal dependencies. Install them with:

```bash
# Install the package with test dependencies
pip install -e ".[test]"
```

This installs:
- `pandas` - For CSV data analysis (used in analyze-csv.py)
- `pytest` - For running tests
- `pytest-cov` - For measuring test coverage

## How to Run the Code

### Running Individual Examples

Each Python file can be run independently. Simply execute:

```bash
# Run any example file
python variables.py
python operators.py
python arrays.py
# ... and so on
```

### Expected Output Example

When you run `variables.py`, you should see output like:

```
Assign a string value to a variable

Office A

----------------------------------------------
Assign a multiple line string value to a variable

Office A

Office B

----------------------------------------------
Assign an integer value to a variable

office_sales is type: <class 'int'>
...
```

### Running All Examples

To run all examples sequentially:

```bash
python test_all.py
```

This will execute each Python file and verify it runs without errors.

## Running Tests

This project has comprehensive tests to ensure all code works correctly.

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage Report

```bash
pytest --cov --cov-report=term
```

This shows which lines of code are tested.

### Run Tests with Detailed HTML Coverage Report

```bash
pytest --cov --cov-report=html
```

Then open `htmlcov/index.html` in your web browser to see a detailed coverage report.

### Expected Test Output

You should see something like:

```
======================== test session starts =========================
collected 38 tests

test_python_learning.py::TestVariables::test_variables_runs_without_error PASSED
test_python_learning.py::TestVariables::test_variables_output_contains_types PASSED
...
======================== 38 passed in 2.45s =========================

---------- coverage: ----------
Name                         Stmts   Miss  Cover
------------------------------------------------
arrays.py                       15      0   100%
classes_and_objects.py           6      0   100%
control_structures.py            9      0   100%
...
------------------------------------------------
TOTAL                          123      0   100%
```

## Troubleshooting

### "python: command not found"

Try using `python3` instead of `python`:

```bash
python3 variables.py
```

### "No module named 'pandas'"

Make sure you installed the dependencies:

```bash
pip install -e ".[test]"
```

### Import Errors

These examples are standalone scripts, not modules. Don't try to import them from other Python files. Run them directly instead.

## Learning Path

If you're new to Python, we recommend going through the files in this order:

1. `comments.py` - Understand how to write comments
2. `variables.py` - Learn about data types
3. `operators.py` - Practice with operators
4. `control_structures.py` - Master flow control
5. `arrays.py` - Work with lists
6. `functions.py` - Create reusable code
7. `exception_handling.py` - Handle errors
8. `classes_and_objects.py` - Learn object-oriented basics
9. `lambdas.py` - Explore functional programming

## Additional Resources

- **Blog Post**: <https://jeffbailey.us/blog/2020/05/26/learn-python/>
- **Python Official Tutorial**: <https://docs.python.org/3/tutorial/>
- **Python Documentation**: <https://docs.python.org/3/>

## Questions or Issues?

If you find any issues or have questions about the code, please open an issue on the [GitHub repository](https://github.com/jeffabailey/learn).
