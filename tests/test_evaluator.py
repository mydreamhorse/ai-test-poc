import pytest
from unittest.mock import patch
from src.evaluator import evaluate_script


class TestEvaluateScript:
    """Test cases for the evaluate_script function."""
    
    def test_evaluate_script_valid_complete_script(self):
        """Test evaluation of a script with both pytest import and test function."""
        script = """
import pytest
from src.custom_test_api import *

def test_example():
    setup_test_environment()
    assert True
    teardown_test_environment()
"""
        result = evaluate_script(script)
        
        assert 'score' in result
        assert 'feedback' in result
        assert 'passed_checks' in result
        assert 0.7 <= result['score'] <= 1.0  # Should be high score
        assert 'pytest_import_found' in result['passed_checks']
        assert 'test_function_defined' in result['passed_checks']
        assert len(result['passed_checks']) == 2
        assert 'plausible' in result['feedback'].lower()
    
    def test_evaluate_script_missing_pytest_import(self):
        """Test evaluation of a script missing pytest import."""
        script = """
def test_example():
    assert True
"""
        result = evaluate_script(script)
        
        assert 0.3 <= result['score'] <= 0.6  # Should be medium score
        assert 'pytest_import_found' not in result['passed_checks']
        assert 'test_function_defined' in result['passed_checks']
        assert len(result['passed_checks']) == 1
        assert 'missing' in result['feedback'].lower()
        assert 'import pytest' in result['feedback']
    
    def test_evaluate_script_missing_test_function(self):
        """Test evaluation of a script missing test function definition."""
        script = """
import pytest
# Some other code but no test function
a = 1 + 1
"""
        result = evaluate_script(script)
        
        assert 0.3 <= result['score'] <= 0.6  # Should be medium score
        assert 'pytest_import_found' in result['passed_checks']
        assert 'test_function_defined' not in result['passed_checks']
        assert len(result['passed_checks']) == 1
        assert 'missing' in result['feedback'].lower()
        assert 'def test_' in result['feedback']
    
    def test_evaluate_script_completely_invalid(self):
        """Test evaluation of a script with neither pytest import nor test function."""
        script = """
print("This is not a test script")
x = 42
"""
        result = evaluate_script(script)
        
        assert 0.0 <= result['score'] <= 0.2  # Should be very low score
        assert len(result['passed_checks']) == 0
        assert 'invalid' in result['feedback'].lower()
        assert 'import pytest' in result['feedback']
        assert 'def test_' in result['feedback']
    
    def test_evaluate_script_empty_script(self):
        """Test evaluation of an empty script."""
        script = ""
        result = evaluate_script(script)
        
        assert 0.0 <= result['score'] <= 0.2  # Should be very low score
        assert len(result['passed_checks']) == 0
        assert 'invalid' in result['feedback'].lower()
    
    def test_evaluate_script_with_test_case_description(self):
        """Test evaluation with test case description provided."""
        script = """
import pytest
def test_login():
    pass
"""
        description = "Test user login functionality"
        result = evaluate_script(script, description)
        
        assert description in result['feedback']
        assert 'consider' in result['feedback'].lower()
    
    def test_evaluate_script_multiple_test_functions(self):
        """Test that script with multiple test functions is recognized."""
        script = """
import pytest

def test_login():
    pass

def test_logout():
    pass

def helper_function():
    pass
"""
        result = evaluate_script(script)
        
        assert 'test_function_defined' in result['passed_checks']
        assert 'pytest_import_found' in result['passed_checks']
        assert 0.7 <= result['score'] <= 1.0
    
    def test_evaluate_script_test_function_with_spaces(self):
        """Test that test function with various spacing is recognized."""
        script = """
import pytest

def   test_with_spaces  ():
    pass
"""
        result = evaluate_script(script)
        
        assert 'test_function_defined' in result['passed_checks']
    
    def test_evaluate_script_pytest_import_variations(self):
        """Test that various pytest import styles are recognized."""
        scripts = [
            "import pytest",
            "import pytest as pt",
            "import pytest\nimport other_module",
            "from pytest import fixture\nimport pytest"
        ]
        
        for script in scripts:
            result = evaluate_script(script)
            assert 'pytest_import_found' in result['passed_checks']
    
    def test_evaluate_script_case_sensitivity(self):
        """Test that function names are case sensitive."""
        script = """
import pytest

def Test_Example():  # Wrong case
    pass

def TEST_EXAMPLE():  # Wrong case
    pass
"""
        result = evaluate_script(script)
        
        assert 'test_function_defined' not in result['passed_checks']
    
    def test_evaluate_script_score_randomness(self):
        """Test that scores have some randomness within expected ranges."""
        script = """
import pytest
def test_example():
    pass
"""
        
        scores = []
        for _ in range(10):
            result = evaluate_script(script)
            scores.append(result['score'])
        
        # All scores should be in the high range
        assert all(0.7 <= score <= 1.0 for score in scores)
        # There should be some variation (not all identical)
        assert len(set(scores)) > 1
    
    def test_evaluate_script_score_rounding(self):
        """Test that scores are properly rounded to 2 decimal places."""
        script = """
import pytest
def test_example():
    pass
"""
        result = evaluate_script(script)
        
        # Check that score has at most 2 decimal places
        score_str = str(result['score'])
        if '.' in score_str:
            decimal_places = len(score_str.split('.')[1])
            assert decimal_places <= 2
    
    @patch('random.uniform')
    def test_evaluate_script_deterministic_with_mocked_random(self, mock_random):
        """Test evaluation with mocked random to ensure deterministic behavior."""
        mock_random.return_value = 0.85
        
        script = """
import pytest
def test_example():
    pass
"""
        result = evaluate_script(script)
        
        assert result['score'] == 0.85
        assert len(result['passed_checks']) == 2
        mock_random.assert_called_once_with(0.7, 1.0)