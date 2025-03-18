#!/usr/bin/env python3
import os
import subprocess
import sys
from typing import Dict, List, Tuple

class TestResult:
    def __init__(self, file_name: str, success: bool, output: str, error: str = None):
        self.file_name = file_name
        self.success = success
        self.output = output
        self.error = error

def get_python_files() -> List[str]:
    """Get all Python files in the current directory except test files."""
    return [f for f in os.listdir('.')
            if f.endswith('.py')
            and not f.startswith('test_')
            and not f == 'main.py']

def run_file(file_path: str) -> TestResult:
    """Run a Python file and return the result."""
    try:
        # Run the file and capture output
        result = subprocess.run([sys.executable, file_path],
                              capture_output=True,
                              text=True,
                              timeout=10)  # 10 second timeout
        
        success = result.returncode == 0
        return TestResult(
            file_name=file_path,
            success=success,
            output=result.stdout,
            error=result.stderr if result.stderr else None
        )
    except subprocess.TimeoutExpired:
        return TestResult(
            file_name=file_path,
            success=False,
            output="",
            error="Timeout: Script took too long to execute"
        )
    except Exception as e:
        return TestResult(
            file_name=file_path,
            success=False,
            output="",
            error=str(e)
        )

def verify_file_output(result: TestResult) -> List[str]:
    """Verify the output of a file based on its type."""
    issues = []
    
    # Basic verification that the file produced some output
    if not result.output.strip():
        issues.append(f"{result.file_name}: No output produced")
        
    # File-specific verifications
    if result.file_name == 'variables.py':
        if 'type: <class' not in result.output:
            issues.append(f"{result.file_name}: Missing type information in output")
    
    elif result.file_name == 'operators.py':
        if 'Arithmetic Operators' not in result.output:
            issues.append(f"{result.file_name}: Missing arithmetic operators section")
        if 'Assignment Operators' not in result.output:
            issues.append(f"{result.file_name}: Missing assignment operators section")
    
    elif result.file_name == 'arrays.py':
        if 'office array' not in result.output.lower():
            issues.append(f"{result.file_name}: Missing array demonstration")
    
    elif result.file_name == 'classes_and_objects.py':
        if 'Office Object Properties' not in result.output:
            issues.append(f"{result.file_name}: Missing class demonstration")
    
    return issues

def print_results(results: List[TestResult], issues: Dict[str, List[str]]):
    """Print the test results in a formatted way."""
    print("\n=== Python Files Test Results ===\n")
    
    total_files = len(results)
    successful_files = sum(1 for r in results if r.success)
    
    for result in results:
        status = "✅ PASS" if result.success else "❌ FAIL"
        print(f"{status} - {result.file_name}")
        
        if not result.success and result.error:
            print(f"  Error: {result.error}")
        
        if result.file_name in issues and issues[result.file_name]:
            print("  Issues found:")
            for issue in issues[result.file_name]:
                print(f"  - {issue}")
        
        print()
    
    print(f"Summary: {successful_files}/{total_files} files passed")
    print("\nNote: This test suite verifies basic execution and output patterns.")
    print("For more detailed testing, consider adding specific unit tests.")

def main():
    # Get all Python files
    python_files = get_python_files()
    
    if not python_files:
        print("No Python files found to test!")
        return
    
    # Run tests
    results = []
    issues = {}
    
    for file in python_files:
        print(f"Testing {file}...")
        result = run_file(file)
        results.append(result)
        
        if result.success:
            file_issues = verify_file_output(result)
            if file_issues:
                issues[file] = file_issues
    
    # Print results
    print_results(results, issues)

if __name__ == "__main__":
    main() 