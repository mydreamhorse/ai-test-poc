import random
import re

def evaluate_script(script_content: str, test_case_description: str = "") -> dict:
    """
    Simulates the evaluation of a generated Pytest script.

    For this Proof of Concept, it performs basic checks like the presence
    of 'import pytest' and a test function definition.

    Args:
        script_content: The string content of the Pytest script.
        test_case_description: Optional original test case description
                               to provide more context in feedback.

    Returns:
        A dictionary containing:
            'score': A float score (0.0-1.0) representing plausibility.
            'feedback': A string with evaluation feedback.
            'passed_checks': A list of strings for checks that passed.
    """
    print(f"Performing dummy evaluation for script (first 100 chars): '{script_content[:100]}...'")
    if test_case_description:
        print(f"With test case description: '{test_case_description}'")

    passed_checks = []
    score = 0.0
    feedback = ""

    # Check 1: Pytest import
    if "import pytest" in script_content:
        passed_checks.append('pytest_import_found')
    
    # Check 2: Test function definition (basic check for 'def test_')
    if re.search(r"def\s+test_", script_content):
        passed_checks.append('test_function_defined')

    num_passed = len(passed_checks)

    if num_passed == 2:
        score = random.uniform(0.7, 1.0)
        feedback = "Script looks plausible and contains key Pytest elements."
        if test_case_description:
            feedback += f" Consider if all aspects of '{test_case_description}' are covered."
    elif num_passed == 1:
        score = random.uniform(0.3, 0.6)
        feedback = "Script is partially valid but missing some key elements. "
        if 'pytest_import_found' not in passed_checks:
            feedback += "Missing 'import pytest'. "
        if 'test_function_defined' not in passed_checks:
            feedback += "No 'def test_' function found. "
    else:
        score = random.uniform(0.0, 0.2)
        feedback = "Script is likely invalid. Missing 'import pytest' and 'def test_' function definition."

    return {
        'score': round(score, 2), # Round for cleaner output
        'feedback': feedback.strip(),
        'passed_checks': passed_checks
    }

if __name__ == '__main__':
    sample_valid_script = """
import pytest
from src.custom_test_api import *

def test_example_case():
    setup_test_environment()
    navigate_to_url("https://example.com")
    verify_element_exists("main_page_header")
    teardown_test_environment()
"""
    sample_invalid_script_no_import = """
def test_missing_import():
    print("This will not run with pytest easily")
"""

    sample_invalid_script_no_test_def = """
import pytest
# No test functions defined
a = 1 + 1
"""
    sample_empty_script = ""

    print("--- Evaluating Valid Script ---")
    eval_result1 = evaluate_script(sample_valid_script, "User sees main page header on example.com")
    print(f"Evaluation Result: {eval_result1}\\n")

    print("--- Evaluating Script Missing Import ---")
    eval_result2 = evaluate_script(sample_invalid_script_no_import)
    print(f"Evaluation Result: {eval_result2}\\n")

    print("--- Evaluating Script Missing Test Definition ---")
    eval_result3 = evaluate_script(sample_invalid_script_no_test_def, "A simple test")
    print(f"Evaluation Result: {eval_result3}\\n")
    
    print("--- Evaluating Empty Script ---")
    eval_result4 = evaluate_script(sample_empty_script)
    print(f"Evaluation Result: {eval_result4}\\n")
