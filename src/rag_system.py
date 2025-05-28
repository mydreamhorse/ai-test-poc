import os
import re
from collections import Counter

def load_rag_data(data_dir: str) -> list[dict]:
    """
    Loads RAG data from .txt files in the specified directory.

    Each .txt file is expected to contain a "Natural Language Test Case:"
    section and an "Ideal Pytest Script:" section.

    Args:
        data_dir: The directory containing the .txt data files.

    Returns:
        A list of dictionaries, where each dictionary has keys
        'filename', 'natural_language_case', and 'ideal_script'.
    """
    rag_data = []
    if not os.path.isdir(data_dir):
        print(f"Error: Data directory '{data_dir}' not found.")
        return rag_data

    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                nl_match = re.search(r"Natural Language Test Case:\s*(.*?)\s*Ideal Pytest Script:", content, re.DOTALL | re.IGNORECASE)
                script_match = re.search(r"Ideal Pytest Script:\s*(.*)", content, re.DOTALL | re.IGNORECASE)

                if nl_match and script_match:
                    natural_language_case = nl_match.group(1).strip()
                    ideal_script = script_match.group(1).strip()
                    rag_data.append({
                        'filename': filename,
                        'natural_language_case': natural_language_case,
                        'ideal_script': ideal_script
                    })
                else:
                    print(f"Warning: Could not parse '{filename}'. Skipping.")
            except Exception as e:
                print(f"Error reading or parsing file {filename}: {e}")
    return rag_data

def retrieve_relevant_examples(natural_language_query: str, rag_data: list[dict], num_examples: int = 1) -> list[dict]:
    """
    Retrieves relevant examples from RAG data based on a natural language query.

    Implements a heuristic for "invalid" or "error" queries, otherwise uses
    basic keyword matching.

    Args:
        natural_language_query: The user's natural language test case query.
        rag_data: A list of dictionaries loaded by load_rag_data.
        num_examples: The number of top examples to return.

    Returns:
        A list containing the top num_examples relevant dictionaries.
    """
    if not rag_data:
        return []

    # Heuristic for "invalid" or "error"
    query_lower = natural_language_query.lower()
    if "invalid" in query_lower or "error" in query_lower:
        invalid_examples = [doc for doc in rag_data if "invalid" in doc['filename'].lower()]
        if invalid_examples:
            return invalid_examples[:num_examples]

    # Basic keyword matching
    query_words = set(re.findall(r'\w+', query_lower))
    if not query_words: # if query is empty or only punctuation
        return rag_data[:num_examples] # return first example(s) as default

    scored_docs = []
    for doc in rag_data:
        doc_words = set(re.findall(r'\w+', doc['natural_language_case'].lower()))
        common_words = query_words.intersection(doc_words)
        score = len(common_words)
        scored_docs.append({'doc': doc, 'score': score})

    # Sort by score in descending order
    scored_docs.sort(key=lambda x: x['score'], reverse=True)

    return [item['doc'] for item in scored_docs[:num_examples]]

if __name__ == '__main__':
    # Create dummy data for local testing
    dummy_data_dir = "../../data_for_rag" # Adjusted path for local execution
    
    # Ensure dummy files exist (mirroring previous setup)
    if not os.path.exists(dummy_data_dir):
        os.makedirs(dummy_data_dir)

    dummy_login_content = """
Natural Language Test Case:
Verify that a user can successfully log in with valid credentials and is redirected to the dashboard. The user should then see a welcome message.

Ideal Pytest Script:
import pytest
from src.custom_test_api import *

def test_successful_login_and_dashboard_welcome():
    setup_test_environment()
    navigate_to_url("https://example.com/login")
    input_text("username", "valid_user")
    input_text("password", "valid_pass")
    click_element("login_submit_button")
    verify_element_exists("dashboard_title")
    verify_text("user_greeting", "Hello, valid_user!")
    teardown_test_environment()
"""
    with open(os.path.join(dummy_data_dir, "login_test.txt"), "w") as f:
        f.write(dummy_login_content)

    dummy_invalid_login_content = """
Natural Language Test Case:
Test that a user attempting to log in with invalid credentials receives an error message and remains on the login page.

Ideal Pytest Script:
import pytest
from src.custom_test_api import *

def test_invalid_login_attempt():
    setup_test_environment()
    navigate_to_url("https://example.com/login")
    input_text("username", "invalid_user")
    input_text("password", "wrong_pass")
    click_element("login_submit_button")
    verify_element_exists("error_message_login")
    verify_text("error_message_login", "Invalid credentials, please try again.")
    teardown_test_environment()
"""
    with open(os.path.join(dummy_data_dir, "invalid_login_test.txt"), "w") as f:
        f.write(dummy_invalid_login_content)
    
    print(f"Attempting to load RAG data from: {os.path.abspath(dummy_data_dir)}")
    loaded_data = load_rag_data(dummy_data_dir)
    print(f"Loaded {len(loaded_data)} RAG documents.")
    for item in loaded_data:
        print(f"  - {item['filename']}")
        # print(f"    NL: {item['natural_language_case'][:50]}...")
        # print(f"    Script: {item['ideal_script'][:60]}...")

    print("\\n--- Testing Retrieval ---")
    
    query1 = "Test user login"
    retrieved1 = retrieve_relevant_examples(query1, loaded_data)
    print(f"Query: '{query1}' -> Retrieved: {[doc['filename'] for doc in retrieved1]}")

    query2 = "User login with invalid password"
    retrieved2 = retrieve_relevant_examples(query2, loaded_data)
    print(f"Query: '{query2}' -> Retrieved: {[doc['filename'] for doc in retrieved2]}")

    query3 = "Check for an error message on bad login"
    retrieved3 = retrieve_relevant_examples(query3, loaded_data, num_examples=1)
    print(f"Query: '{query3}' -> Retrieved: {[doc['filename'] for doc in retrieved3]}")
    
    query4 = "This is a completely unrelated query"
    retrieved4 = retrieve_relevant_examples(query4, loaded_data, num_examples=1)
    print(f"Query: '{query4}' -> Retrieved (defaulting): {[doc['filename'] for doc in retrieved4]}")

    # Clean up dummy files
    # os.remove(os.path.join(dummy_data_dir, "login_test.txt"))
    # os.remove(os.path.join(dummy_data_dir, "invalid_login_test.txt"))
    # if not os.listdir(dummy_data_dir): # remove dir if empty
    #     os.rmdir(dummy_data_dir)
    pass
