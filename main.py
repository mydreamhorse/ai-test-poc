import os
from dotenv import load_dotenv
import src.rag_system as rag_system
import src.llm_interface as llm_interface
import src.evaluator as evaluator
import src.dspy_optimizer as dspy_optimizer # For conceptual demonstration

def main():
    print("--- Starting Proof of Concept (PoC) for AI Test Generation ---")

    # 加载.env文件中的环境变量
    load_dotenv()
    
    # 获取OpenAI API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables or .env file.")
        print("Please set your OpenAI API key in .env file:")
        print("OPENAI_API_KEY=your-api-key")
        return

    # 1. Define a sample natural language test case
    print("\n[Step 1: Sample Natural Language Test Case]")
    natural_language_test_case = (
        "Verify that a new user can register successfully by filling out the "
        "registration form (username, email, password), submitting it, "
        "and then is automatically logged in, seeing a personalized welcome "
        "message on their dashboard like 'Welcome, new_username!'."
    )
    print(f"Test Case: \"{natural_language_test_case}\"")

    # --- RAG System Integration ---
    print("\n[Step 2: RAG System - Retrieving Examples]")
    rag_data_directory = "data_for_rag"
    
    # Ensure RAG data directory exists (it should from previous steps)
    if not os.path.isdir(rag_data_directory):
        print(f"Error: RAG data directory '{rag_data_directory}' not found. Make sure it's created and populated.")
        # As a fallback for PoC, create dummy files if they are missing, so the script can run.
        # This mirrors the dummy data creation in rag_system.py's __main__ block.
        print(f"Attempting to create dummy RAG data in '{rag_data_directory}' for PoC continuation...")
        os.makedirs(rag_data_directory, exist_ok=True)
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
        with open(os.path.join(rag_data_directory, "login_test.txt"), "w") as f:
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
        with open(os.path.join(rag_data_directory, "invalid_login_test.txt"), "w") as f:
            f.write(dummy_invalid_login_content)
        print(f"Dummy RAG data created in '{rag_data_directory}'.")


    all_rag_examples = rag_system.load_rag_data(data_dir=rag_data_directory)
    if not all_rag_examples:
        print("Warning: No RAG examples were loaded. Proceeding without them.")
        retrieved_examples_for_prompt = "No relevant examples found by RAG."
    else:
        print(f"Loaded {len(all_rag_examples)} total examples from RAG.")
        relevant_examples = rag_system.retrieve_relevant_examples(
            natural_language_query=natural_language_test_case,
            rag_data=all_rag_examples,
            num_examples=1
        )
        if relevant_examples:
            print(f"Retrieved {len(relevant_examples)} relevant example(s):")
            for i, ex in enumerate(relevant_examples):
                print(f"  Example {i+1} (from {ex['filename']}):")
                print(f"    NL: {ex['natural_language_case'][:100]}...")
                print(f"    Script: {ex['ideal_script'][:100].strip()}...")
            # Format for prompt
            retrieved_examples_for_prompt = "\n\nHere's a relevant example:\n"
            retrieved_examples_for_prompt += f"Natural Language: {relevant_examples[0]['natural_language_case']}\n"
            retrieved_examples_for_prompt += f"Ideal Script: {relevant_examples[0]['ideal_script']}"
        else:
            print("No specific relevant examples found by RAG for this query.")
            retrieved_examples_for_prompt = "No specific relevant examples found by RAG."

    # --- Prompt Construction ---
    print("\n[Step 3: Prompt Construction]")
    # Our llm_interface.generate_test_script currently just prints the prompt.
    # For a more advanced LLM, we would craft a more detailed prompt here.
    # The conceptual prompt in dspy_optimizer.py is more aligned with that.
    # Here, we'll keep it simple as our llm_interface is hardcoded.
    
    # The prompt sent to our current hardcoded llm_interface doesn't actually use the examples.
    # However, we construct it as if it would for future compatibility.
    prompt_for_llm = (
        f"Generate a Pytest script for the following test case:\n"
        f"\"{natural_language_test_case}\"\n"
        f"{retrieved_examples_for_prompt}"
    )
    print(f"Constructed Prompt for LLM:\n---\n{prompt_for_llm}\n---")

    # --- Test Script Generation (using LLM interface) ---
    print("\n[Step 4: Test Script Generation (Real LLM Interface)]")
    try:
        generated_script = llm_interface.generate_test_script(prompt=prompt_for_llm, api_key=api_key)
        print(f"Generated Script:\n---\n{generated_script}\n---")
    except Exception as e:
        print(f"Error generating test script: {str(e)}")
        return

    # --- Save the Generated Script ---
    print("\n[Step 5: Saving Generated Script]")
    generated_tests_dir = "generated_tests"
    if not os.path.exists(generated_tests_dir):
        os.makedirs(generated_tests_dir)
        print(f"Created directory: {generated_tests_dir}")

    script_filename = "test_poc_generated_case.py"
    script_filepath = os.path.join(generated_tests_dir, script_filename)
    try:
        with open(script_filepath, "w") as f:
            f.write(generated_script)
        print(f"Generated script saved to: {os.path.abspath(script_filepath)}")
    except IOError as e:
        print(f"Error saving script to {script_filepath}: {e}")


    # --- Evaluation Step ---
    print("\n[Step 6: Evaluation of Generated Script (Dummy Evaluator)]")
    evaluation_result = evaluator.evaluate_script(
        script_content=generated_script,
        test_case_description=natural_language_test_case
    )
    print(f"Evaluation Score: {evaluation_result['score']}")
    print(f"Evaluation Feedback: {evaluation_result['feedback']}")
    print(f"Passed Checks: {evaluation_result['passed_checks']}")

    # --- DSPy Conceptual Demonstration ---
    print("\n[Step 7: DSPy Conceptual Module Demonstration]")
    print("This demonstrates running the conceptual DSPy module defined in dspy_optimizer.py.")
    
    # Instantiate the conceptual module from dspy_optimizer
    # It will print its own conceptual messages.
    conceptual_dspy_module = dspy_optimizer.ConceptualTestGenerationModule()
    
    # For the PoC, we need to ensure it has RAG data if it's to simulate retrieval
    conceptual_dspy_module.load_rag_data_for_poc(rag_data_directory)

    print(f"\nCalling conceptual_dspy_module.forward() with the test case: \"{natural_language_test_case}\"")
    # The conceptual_dspy_module.forward will print its steps and call our hardcoded llm_interface
    conceptual_script_output = conceptual_dspy_module.forward(natural_language_test_case)
    
    print("\nDSPy Conceptual Module Demonstration - Output:")
    if conceptual_script_output:
        print(f"  Script from conceptual module (first 100 chars): '{conceptual_script_output[:100].strip()}...'")
        # Optionally, evaluate this output too
        conceptual_eval = evaluator.evaluate_script(conceptual_script_output, natural_language_test_case)
        print(f"  Evaluation of conceptual module's script: Score {conceptual_eval['score']}, Feedback: {conceptual_eval['feedback']}")
    else:
        print("  Conceptual DSPy module did not produce a script output in this simulation.")
    
    print("\n--- PoC Workflow Complete ---")

if __name__ == "__main__":
    main()
