import pytest
from unittest.mock import patch
from src.llm_interface import generate_test_script


class TestGenerateTestScript:
    """Test cases for the generate_test_script function."""
    
    @patch('builtins.print')
    def test_generate_test_script_basic(self, mock_print):
        """Test that generate_test_script prints the prompt and returns expected script."""
        prompt = "Test case: User login functionality"
        result = generate_test_script(prompt)
        
        # Verify the prompt was printed
        mock_print.assert_called_once_with(f"Received prompt: {prompt}")
        
        # Verify the returned script contains expected elements
        assert isinstance(result, str)
        assert "import pytest" in result
        assert "from src.custom_test_api import *" in result
        assert "def test_login_and_verify_dashboard():" in result
        assert "setup_test_environment()" in result
        assert "teardown_test_environment()" in result
    
    @patch('builtins.print')
    def test_generate_test_script_empty_prompt(self, mock_print):
        """Test generate_test_script with empty prompt."""
        prompt = ""
        result = generate_test_script(prompt)
        
        mock_print.assert_called_once_with(f"Received prompt: {prompt}")
        
        # Should still return the hardcoded script
        assert isinstance(result, str)
        assert "import pytest" in result
        assert "def test_login_and_verify_dashboard():" in result
    
    @patch('builtins.print')
    def test_generate_test_script_none_prompt(self, mock_print):
        """Test generate_test_script with None prompt."""
        prompt = None
        result = generate_test_script(prompt)
        
        mock_print.assert_called_once_with(f"Received prompt: {prompt}")
        
        # Should still return the hardcoded script
        assert isinstance(result, str)
        assert "import pytest" in result
    
    @patch('builtins.print')
    def test_generate_test_script_long_prompt(self, mock_print):
        """Test generate_test_script with a very long prompt."""
        prompt = "Test case: " + "Very long description " * 100
        result = generate_test_script(prompt)
        
        mock_print.assert_called_once_with(f"Received prompt: {prompt}")
        
        # Should still return the hardcoded script regardless of prompt length
        assert isinstance(result, str)
        assert "import pytest" in result
    
    @patch('builtins.print')
    def test_generate_test_script_special_characters_prompt(self, mock_print):
        """Test generate_test_script with prompt containing special characters."""
        prompt = "Test case: Login with special chars !@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = generate_test_script(prompt)
        
        mock_print.assert_called_once_with(f"Received prompt: {prompt}")
        
        assert isinstance(result, str)
        assert "import pytest" in result
    
    @patch('builtins.print')
    def test_generate_test_script_multiline_prompt(self, mock_print):
        """Test generate_test_script with multiline prompt."""
        prompt = """Test case: 
        1. Navigate to login page
        2. Enter credentials
        3. Verify dashboard"""
        result = generate_test_script(prompt)
        
        mock_print.assert_called_once_with(f"Received prompt: {prompt}")
        
        assert isinstance(result, str)
        assert "import pytest" in result
    
    def test_generate_test_script_return_value_structure(self):
        """Test that the returned script has the expected structure."""
        prompt = "Test case: Basic functionality"
        result = generate_test_script(prompt)
        
        # Check that the script contains all expected components
        expected_components = [
            "import pytest",
            "from src.custom_test_api import *",
            "def test_login_and_verify_dashboard():",
            "setup_test_environment()",
            "navigate_to_url(",
            "input_text(",
            "click_element(",
            "verify_element_exists(",
            "verify_text(",
            "teardown_test_environment()"
        ]
        
        for component in expected_components:
            assert component in result, f"Expected component '{component}' not found in script"
    
    def test_generate_test_script_hardcoded_values(self):
        """Test that the script contains the expected hardcoded values."""
        prompt = "Any prompt"
        result = generate_test_script(prompt)
        
        # Check for specific hardcoded values in the script
        assert "https://example.com/login" in result
        assert "username_field" in result
        assert "password_field" in result
        assert "testuser" in result
        assert "password123" in result
        assert "login_button" in result
        assert "dashboard_header" in result
        assert "welcome_message" in result
        assert "Welcome, testuser!" in result
    
    def test_generate_test_script_consistency(self):
        """Test that the function returns the same script for different prompts."""
        prompts = [
            "Test login",
            "Verify user authentication",
            "Check dashboard access",
            "",
            None
        ]
        
        results = []
        for prompt in prompts:
            result = generate_test_script(prompt)
            results.append(result)
        
        # All results should be identical since it's hardcoded
        for i in range(1, len(results)):
            assert results[i] == results[0], f"Script for prompt {i} differs from first script"
    
    def test_generate_test_script_valid_python_syntax(self):
        """Test that the returned script has valid Python syntax."""
        prompt = "Test case: Example"
        result = generate_test_script(prompt)
        
        # Try to compile the script to check for syntax errors
        try:
            compile(result, '<string>', 'exec')
        except SyntaxError as e:
            pytest.fail(f"Generated script has invalid Python syntax: {e}")
    
    def test_generate_test_script_indentation(self):
        """Test that the returned script has proper indentation."""
        prompt = "Test case: Example"
        result = generate_test_script(prompt)
        
        lines = result.split('\n')
        
        # Find the function definition line
        func_line_index = None
        for i, line in enumerate(lines):
            if "def test_login_and_verify_dashboard():" in line:
                func_line_index = i
                break
        
        assert func_line_index is not None, "Function definition not found"
        
        # Check that function body lines are properly indented
        for i in range(func_line_index + 1, len(lines)):
            line = lines[i]
            if line.strip():  # Skip empty lines
                if not line.startswith('    ') and not line.startswith('\n'):
                    # This might be the end of the function or another top-level statement
                    break
                # Lines inside the function should be indented
                if line.strip() and not line.startswith('    '):
                    pytest.fail(f"Line '{line}' is not properly indented")
    
    @patch('builtins.print')
    def test_generate_test_script_unicode_prompt(self, mock_print):
        """Test generate_test_script with Unicode characters in prompt."""
        prompt = "Test case: Login with émojis 🔐 and ñoñó characters"
        result = generate_test_script(prompt)
        
        mock_print.assert_called_once_with(f"Received prompt: {prompt}")
        
        assert isinstance(result, str)
        assert "import pytest" in result