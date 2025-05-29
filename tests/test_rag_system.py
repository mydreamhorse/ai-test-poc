import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open
from src.rag_system import load_rag_data, retrieve_relevant_examples


class TestLoadRagData:
    """Test cases for the load_rag_data function."""
    
    def test_load_rag_data_nonexistent_directory(self):
        """Test that load_rag_data returns empty list for non-existent directory."""
        result = load_rag_data("nonexistent_directory")
        assert result == []
    
    def test_load_rag_data_empty_directory(self):
        """Test that load_rag_data returns empty list for empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = load_rag_data(temp_dir)
            assert result == []
    
    def test_load_rag_data_valid_file(self):
        """Test that load_rag_data correctly parses a valid file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_case.txt")
            content = """
Natural Language Test Case:
This is a test case for login functionality.

Ideal Pytest Script:
import pytest
def test_login():
    assert True
"""
            with open(test_file, 'w') as f:
                f.write(content)
            
            result = load_rag_data(temp_dir)
            assert len(result) == 1
            assert result[0]['filename'] == 'test_case.txt'
            assert 'This is a test case for login functionality.' in result[0]['natural_language_case']
            assert 'import pytest' in result[0]['ideal_script']
            assert 'def test_login():' in result[0]['ideal_script']
    
    def test_load_rag_data_multiple_files(self):
        """Test that load_rag_data loads multiple valid files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first file
            test_file1 = os.path.join(temp_dir, "login_test.txt")
            content1 = """
Natural Language Test Case:
Test login functionality.

Ideal Pytest Script:
import pytest
def test_login():
    pass
"""
            with open(test_file1, 'w') as f:
                f.write(content1)
            
            # Create second file
            test_file2 = os.path.join(temp_dir, "logout_test.txt")
            content2 = """
Natural Language Test Case:
Test logout functionality.

Ideal Pytest Script:
import pytest
def test_logout():
    pass
"""
            with open(test_file2, 'w') as f:
                f.write(content2)
            
            result = load_rag_data(temp_dir)
            assert len(result) == 2
            filenames = [item['filename'] for item in result]
            assert 'login_test.txt' in filenames
            assert 'logout_test.txt' in filenames
    
    def test_load_rag_data_invalid_format(self):
        """Test that load_rag_data skips files with invalid format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with invalid format
            test_file = os.path.join(temp_dir, "invalid.txt")
            content = "This file doesn't have the expected format"
            with open(test_file, 'w') as f:
                f.write(content)
            
            result = load_rag_data(temp_dir)
            assert result == []
    
    def test_load_rag_data_non_txt_files_ignored(self):
        """Test that load_rag_data ignores non-.txt files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .py file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("print('hello')")
            
            result = load_rag_data(temp_dir)
            assert result == []
    
    def test_load_rag_data_case_insensitive_parsing(self):
        """Test that load_rag_data parsing is case insensitive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_case.txt")
            content = """
natural language test case:
This is a test case.

ideal pytest script:
import pytest
def test_example():
    pass
"""
            with open(test_file, 'w') as f:
                f.write(content)
            
            result = load_rag_data(temp_dir)
            assert len(result) == 1
            assert 'This is a test case.' in result[0]['natural_language_case']
    
    def test_load_rag_data_file_read_error(self):
        """Test that load_rag_data handles file read errors gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")
            # Create the file so it exists
            with open(test_file, 'w') as f:
                f.write("test")
            
            # Now mock open to raise an error only for the load_rag_data function
            with patch('src.rag_system.open', side_effect=IOError("Permission denied")):
                result = load_rag_data(temp_dir)
                assert result == []


class TestRetrieveRelevantExamples:
    """Test cases for the retrieve_relevant_examples function."""
    
    def test_retrieve_relevant_examples_empty_rag_data(self):
        """Test that function returns empty list when rag_data is empty."""
        result = retrieve_relevant_examples("test query", [], num_examples=1)
        assert result == []
    
    def test_retrieve_relevant_examples_invalid_heuristic(self):
        """Test that function prioritizes files with 'invalid' in filename for invalid queries."""
        rag_data = [
            {
                'filename': 'valid_login.txt',
                'natural_language_case': 'Test valid login',
                'ideal_script': 'def test_valid_login(): pass'
            },
            {
                'filename': 'invalid_login.txt',
                'natural_language_case': 'Test invalid login',
                'ideal_script': 'def test_invalid_login(): pass'
            }
        ]
        
        result = retrieve_relevant_examples("Test invalid login", rag_data, num_examples=1)
        assert len(result) == 1
        assert result[0]['filename'] == 'invalid_login.txt'
    
    def test_retrieve_relevant_examples_error_heuristic(self):
        """Test that function prioritizes files with 'invalid' in filename for error queries."""
        rag_data = [
            {
                'filename': 'success_case.txt',
                'natural_language_case': 'Test successful operation',
                'ideal_script': 'def test_success(): pass'
            },
            {
                'filename': 'invalid_case.txt',
                'natural_language_case': 'Test error handling',
                'ideal_script': 'def test_error(): pass'
            }
        ]
        
        result = retrieve_relevant_examples("Test error handling", rag_data, num_examples=1)
        assert len(result) == 1
        assert result[0]['filename'] == 'invalid_case.txt'
    
    def test_retrieve_relevant_examples_keyword_matching(self):
        """Test that function uses keyword matching when no heuristic applies."""
        rag_data = [
            {
                'filename': 'login_test.txt',
                'natural_language_case': 'Test user login functionality',
                'ideal_script': 'def test_login(): pass'
            },
            {
                'filename': 'logout_test.txt',
                'natural_language_case': 'Test user logout functionality',
                'ideal_script': 'def test_logout(): pass'
            }
        ]
        
        result = retrieve_relevant_examples("user login", rag_data, num_examples=1)
        assert len(result) == 1
        assert result[0]['filename'] == 'login_test.txt'
    
    def test_retrieve_relevant_examples_multiple_results(self):
        """Test that function returns multiple results when requested."""
        rag_data = [
            {
                'filename': 'test1.txt',
                'natural_language_case': 'Test login functionality',
                'ideal_script': 'def test1(): pass'
            },
            {
                'filename': 'test2.txt',
                'natural_language_case': 'Test login process',
                'ideal_script': 'def test2(): pass'
            },
            {
                'filename': 'test3.txt',
                'natural_language_case': 'Test logout functionality',
                'ideal_script': 'def test3(): pass'
            }
        ]
        
        result = retrieve_relevant_examples("login", rag_data, num_examples=2)
        assert len(result) == 2
        # Should return the two login-related tests
        filenames = [item['filename'] for item in result]
        assert 'test1.txt' in filenames
        assert 'test2.txt' in filenames
    
    def test_retrieve_relevant_examples_empty_query(self):
        """Test that function returns first examples for empty query."""
        rag_data = [
            {
                'filename': 'test1.txt',
                'natural_language_case': 'First test',
                'ideal_script': 'def test1(): pass'
            },
            {
                'filename': 'test2.txt',
                'natural_language_case': 'Second test',
                'ideal_script': 'def test2(): pass'
            }
        ]
        
        result = retrieve_relevant_examples("", rag_data, num_examples=1)
        assert len(result) == 1
        assert result[0]['filename'] == 'test1.txt'
    
    def test_retrieve_relevant_examples_punctuation_only_query(self):
        """Test that function handles queries with only punctuation."""
        rag_data = [
            {
                'filename': 'test1.txt',
                'natural_language_case': 'First test',
                'ideal_script': 'def test1(): pass'
            }
        ]
        
        result = retrieve_relevant_examples("!@#$%", rag_data, num_examples=1)
        assert len(result) == 1
        assert result[0]['filename'] == 'test1.txt'
    
    def test_retrieve_relevant_examples_scoring_order(self):
        """Test that function returns results in correct score order."""
        rag_data = [
            {
                'filename': 'low_score.txt',
                'natural_language_case': 'Test something else',
                'ideal_script': 'def test_other(): pass'
            },
            {
                'filename': 'high_score.txt',
                'natural_language_case': 'Test user login authentication',
                'ideal_script': 'def test_login(): pass'
            },
            {
                'filename': 'medium_score.txt',
                'natural_language_case': 'Test user registration',
                'ideal_script': 'def test_register(): pass'
            }
        ]
        
        result = retrieve_relevant_examples("user login", rag_data, num_examples=3)
        assert len(result) == 3
        # First result should have highest score (most matching words)
        assert result[0]['filename'] == 'high_score.txt'
    
    def test_retrieve_relevant_examples_no_invalid_files_for_invalid_query(self):
        """Test behavior when query contains 'invalid' but no files have 'invalid' in filename."""
        rag_data = [
            {
                'filename': 'login_test.txt',
                'natural_language_case': 'Test valid login',
                'ideal_script': 'def test_login(): pass'
            }
        ]
        
        result = retrieve_relevant_examples("invalid login test", rag_data, num_examples=1)
        assert len(result) == 1
        # Should fall back to keyword matching
        assert result[0]['filename'] == 'login_test.txt'