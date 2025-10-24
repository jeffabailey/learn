#!/usr/bin/env python3
"""
Comprehensive tests for Python learning content.
Tests verify that all the code examples work correctly and teach the right concepts.
"""
import pytest
import subprocess
import sys
from pathlib import Path


class TestVariables:
    """Test variables.py module"""

    def test_variables_runs_without_error(self):
        """Test that variables.py executes successfully"""
        result = subprocess.run(
            [sys.executable, "variables.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"

    def test_variables_output_contains_types(self):
        """Test that variables.py demonstrates type checking"""
        result = subprocess.run(
            [sys.executable, "variables.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout
        assert "<class 'int'>" in output
        assert "<class 'float'>" in output
        assert "<class 'bool'>" in output


class TestArrays:
    """Test arrays.py module"""

    def test_arrays_runs_without_error(self):
        """Test that arrays.py executes successfully"""
        result = subprocess.run(
            [sys.executable, "arrays.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"

    def test_arrays_accesses_first_element(self):
        """Test that arrays.py correctly accesses array element 0"""
        result = subprocess.run(
            [sys.executable, "arrays.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        # Should output the first element, not the entire array
        assert "Office A" in result.stdout
        # Should not output the list representation with brackets
        lines = result.stdout.split('\n')
        accessing_section = False
        for i, line in enumerate(lines):
            if "Accessing array item 0" in line:
                accessing_section = True
            elif accessing_section and "Found" in line:
                # This line should contain just "Office A", not a list
                assert "[" not in line or "]" not in line


class TestOperators:
    """Test operators.py module"""

    def test_operators_runs_without_error(self):
        """Test that operators.py executes successfully"""
        result = subprocess.run(
            [sys.executable, "operators.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"

    def test_exponentiation_operator(self):
        """Test that exponentiation operator shows correct result (2**3=8)"""
        result = subprocess.run(
            [sys.executable, "operators.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        # 2 ** 3 should equal 8, not 6 (which would be 2 * 3)
        assert "2 ** 3 = 8" in result.stdout or "2 **= 8" in result.stdout

    def test_floor_division_operator(self):
        """Test that floor division shows correct calculation"""
        result = subprocess.run(
            [sys.executable, "operators.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        # Should show the actual value being divided
        assert "78125.0 //=" in result.stdout


class TestFunctions:
    """Test functions.py module"""

    def test_functions_runs_with_existing_file(self):
        """Test that functions.py successfully reads example.csv"""
        result = subprocess.run(
            [sys.executable, "functions.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
        assert "Found file" in result.stdout or "Office" in result.stdout

    def test_function_parameter_is_used(self):
        """Test that file_check function uses its parameter"""
        # Create a test to verify the function parameter is actually used
        import tempfile
        import os

        test_content = "Test content"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_content)
            temp_file = f.name

        try:
            # Import and test the function directly
            sys.path.insert(0, str(Path(__file__).parent))
            from functions import file_check

            result = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, '{Path(__file__).parent}'); "
                 f"from functions import file_check; file_check('{temp_file}')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert test_content in result.stdout
        finally:
            os.unlink(temp_file)


class TestControlStructures:
    """Test control_structures.py module"""

    def test_control_structures_runs_without_error(self):
        """Test that control_structures.py executes successfully"""
        result = subprocess.run(
            [sys.executable, "control_structures.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0


class TestClassesAndObjects:
    """Test classes_and_objects.py module"""

    def test_classes_runs_without_error(self):
        """Test that classes_and_objects.py executes successfully"""
        result = subprocess.run(
            [sys.executable, "classes_and_objects.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
        assert "Office A" in result.stdout
        assert "Portland, Oregon" in result.stdout


class TestLambdas:
    """Test lambdas.py module"""

    def test_lambdas_runs_without_error(self):
        """Test that lambdas.py executes successfully"""
        result = subprocess.run(
            [sys.executable, "lambdas.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0

    def test_lambdas_finds_max_sales(self):
        """Test that lambda correctly finds office with highest sales"""
        result = subprocess.run(
            [sys.executable, "lambdas.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        # Office C has sales of 9, which is the highest
        assert "Office C" in result.stdout and "9" in result.stdout


class TestExceptionHandling:
    """Test exception_handling.py module"""

    def test_exception_handling_runs_without_error(self):
        """Test that exception_handling.py executes successfully"""
        result = subprocess.run(
            [sys.executable, "exception_handling.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0

    def test_exception_handling_catches_missing_file(self):
        """Test that exception_handling.py properly handles missing file"""
        result = subprocess.run(
            [sys.executable, "exception_handling.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        # Should show error message for missing file
        assert "Error" in result.stdout or "does not exist" in result.stdout


class TestComments:
    """Test comments.py module"""

    def test_comments_runs_without_error(self):
        """Test that comments.py executes successfully"""
        result = subprocess.run(
            [sys.executable, "comments.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0


class TestCodeQuality:
    """Test code quality and best practices"""

    def test_no_debug_prints_in_variables(self):
        """Test that variables.py doesn't contain debug print statements"""
        with open(Path(__file__).parent / "variables.py", 'r') as f:
            content = f.read()
        # Should not contain random debug prints like 'yo'
        assert 'print("yo")' not in content

    def test_correct_grammar_in_variables(self):
        """Test that variables.py has correct grammar"""
        with open(Path(__file__).parent / "variables.py", 'r') as f:
            content = f.read()
        # Should say "a boolean" not "an boolean"
        assert "'Assign a boolean value to a variable'" in content
        assert "'Assign an boolean value to a variable'" not in content

    def test_no_typos_in_comments(self):
        """Test that variables.py comments don't have typos"""
        with open(Path(__file__).parent / "variables.py", 'r') as f:
            content = f.read()
        # Should not have .abs suffix on comment
        assert "variables.abs" not in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
