import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from src import rag_system, llm_interface, evaluator


class TestIntegration:
    """Integration tests for the AI test generation system."""
    
    def test_end_to_end_workflow(self):
        """Test the complete workflow from RAG data loading to script evaluation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test RAG data
            test_file = os.path.join(temp_dir, "login_test.txt")
            content = """
Natural Language Test Case:
Test user login with valid credentials.

Ideal Pytest Script:
import pytest
from src.custom_test_api import *

def test_valid_login():
    setup_test_environment()
    navigate_to_url("https://example.com/login")
    input_text("username", "testuser")
    input_text("password", "testpass")
    click_element("login_button")
    verify_element_exists("dashboard")
    teardown_test_environment()
"""
            with open(test_file, 'w') as f:
                f.write(content)
            
            # Step 1: Load RAG data
            rag_data = rag_system.load_rag_data(temp_dir)
            assert len(rag_data) == 1
            assert rag_data[0]['filename'] == 'login_test.txt'
            
            # Step 2: Retrieve relevant examples
            query = "user login functionality"
            relevant_examples = rag_system.retrieve_relevant_examples(query, rag_data, num_examples=1)
            assert len(relevant_examples) == 1
            assert 'login' in relevant_examples[0]['natural_language_case'].lower()
            
            # Step 3: Generate test script
            prompt = f"Generate test for: {query}\nExample: {relevant_examples[0]['natural_language_case']}"
            generated_script = llm_interface.generate_test_script(prompt)
            assert "import pytest" in generated_script
            assert "def test_" in generated_script
            
            # Step 4: Evaluate generated script
            evaluation = evaluator.evaluate_script(generated_script, query)
            assert 'score' in evaluation
            assert 'feedback' in evaluation
            assert 'passed_checks' in evaluation
            assert evaluation['score'] >= 0.0
            assert evaluation['score'] <= 1.0
    
    def test_rag_to_llm_integration(self):
        """Test integration between RAG system and LLM interface."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple test files
            files_data = [
                ("valid_login.txt", "Test valid login", "def test_valid_login(): pass"),
                ("invalid_login.txt", "Test invalid login", "def test_invalid_login(): pass"),
                ("registration.txt", "Test user registration", "def test_registration(): pass")
            ]
            
            for filename, nl_case, script in files_data:
                filepath = os.path.join(temp_dir, filename)
                content = f"""
Natural Language Test Case:
{nl_case}

Ideal Pytest Script:
import pytest
{script}
"""
                with open(filepath, 'w') as f:
                    f.write(content)
            
            # Load RAG data
            rag_data = rag_system.load_rag_data(temp_dir)
            assert len(rag_data) == 3
            
            # Test retrieval for different queries
            test_cases = [
                ("invalid login", "invalid_login.txt"),
                ("user registration", "registration.txt"),
                ("valid login", "valid_login.txt")
            ]
            
            for query, expected_file in test_cases:
                relevant = rag_system.retrieve_relevant_examples(query, rag_data, num_examples=1)
                assert len(relevant) == 1
                assert relevant[0]['filename'] == expected_file
                
                # Generate script using the retrieved example
                prompt = f"Query: {query}\nExample: {relevant[0]['natural_language_case']}"
                script = llm_interface.generate_test_script(prompt)
                assert isinstance(script, str)
                assert len(script) > 0
    
    def test_llm_to_evaluator_integration(self):
        """Test integration between LLM interface and evaluator."""
        test_prompts = [
            "Generate a simple test",
            "Create a login test",
            "Test user authentication",
            ""  # Empty prompt
        ]
        
        for prompt in test_prompts:
            # Generate script
            script = llm_interface.generate_test_script(prompt)
            
            # Evaluate script
            evaluation = evaluator.evaluate_script(script, prompt)
            
            # Verify evaluation structure
            assert isinstance(evaluation, dict)
            assert 'score' in evaluation
            assert 'feedback' in evaluation
            assert 'passed_checks' in evaluation
            
            # Since the LLM interface returns a hardcoded valid script,
            # the evaluation should always be positive
            assert evaluation['score'] > 0.5
            assert 'pytest_import_found' in evaluation['passed_checks']
            assert 'test_function_defined' in evaluation['passed_checks']
    
    def test_rag_system_with_empty_directory(self):
        """Test RAG system behavior with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rag_data = rag_system.load_rag_data(temp_dir)
            assert rag_data == []
            
            # Retrieval should return empty list
            relevant = rag_system.retrieve_relevant_examples("any query", rag_data)
            assert relevant == []
    
    def test_rag_system_with_malformed_files(self):
        """Test RAG system behavior with malformed files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files with various malformed content
            malformed_files = [
                ("incomplete.txt", "Natural Language Test Case:\nMissing script section"),
                ("no_sections.txt", "Just some random text without proper sections"),
                ("empty.txt", ""),
                ("only_script.txt", "Ideal Pytest Script:\ndef test(): pass")
            ]
            
            for filename, content in malformed_files:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(content)
            
            rag_data = rag_system.load_rag_data(temp_dir)
            # Should return empty list since no files have proper format
            assert rag_data == []
    
    def test_evaluator_with_various_script_qualities(self):
        """Test evaluator with scripts of different qualities."""
        test_scripts = [
            # Perfect script
            """
import pytest
from src.custom_test_api import *

def test_example():
    setup_test_environment()
    assert True
    teardown_test_environment()
""",
            # Missing import
            """
def test_example():
    assert True
""",
            # Missing test function
            """
import pytest
# No test function
x = 1
""",
            # Completely invalid
            """
print("Not a test")
""",
            # Empty script
            ""
        ]
        
        expected_score_ranges = [
            (0.7, 1.0),  # Perfect script
            (0.3, 0.6),  # Missing import
            (0.3, 0.6),  # Missing test function
            (0.0, 0.2),  # Invalid
            (0.0, 0.2)   # Empty
        ]
        
        for script, (min_score, max_score) in zip(test_scripts, expected_score_ranges):
            evaluation = evaluator.evaluate_script(script)
            assert min_score <= evaluation['score'] <= max_score, \
                f"Score {evaluation['score']} not in expected range [{min_score}, {max_score}] for script: {script[:50]}..."
    
    @patch('builtins.print')
    def test_integration_with_mocked_output(self, mock_print):
        """Test integration while suppressing print output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_file = os.path.join(temp_dir, "test.txt")
            content = """
Natural Language Test Case:
Simple test case.

Ideal Pytest Script:
import pytest
def test_simple():
    pass
"""
            with open(test_file, 'w') as f:
                f.write(content)
            
            # Run the workflow
            rag_data = rag_system.load_rag_data(temp_dir)
            relevant = rag_system.retrieve_relevant_examples("simple test", rag_data)
            script = llm_interface.generate_test_script("test prompt")
            evaluation = evaluator.evaluate_script(script)
            
            # Verify the workflow completed successfully
            assert len(rag_data) == 1
            assert len(relevant) == 1
            assert "import pytest" in script
            assert evaluation['score'] > 0
            
            # Verify that print was called (functions do print their operations)
            assert mock_print.called
    
    def test_workflow_with_nonexistent_rag_directory(self):
        """Test workflow behavior when RAG directory doesn't exist."""
        nonexistent_dir = "/path/that/does/not/exist"
        
        # RAG system should handle this gracefully
        rag_data = rag_system.load_rag_data(nonexistent_dir)
        assert rag_data == []
        
        # Retrieval should return empty
        relevant = rag_system.retrieve_relevant_examples("any query", rag_data)
        assert relevant == []
        
        # LLM should still work
        script = llm_interface.generate_test_script("test without rag")
        assert "import pytest" in script
        
        # Evaluation should still work
        evaluation = evaluator.evaluate_script(script)
        assert evaluation['score'] > 0