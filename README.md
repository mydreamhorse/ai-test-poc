# AI-Powered Test Case to Pytest Script Generation PoC

## 1. Overview/Purpose

The goal of this project is to build a Proof of Concept (PoC) system that utilizes a Large Language Model (LLM) to understand natural language test cases and automatically generate corresponding Pytest automation scripts.

This PoC explores the integration of several key concepts:
*   **Retrieval Augmented Generation (RAG):** To provide the LLM with relevant context and examples, improving the quality and relevance of generated scripts.
*   **DSPy for Optimization (Conceptual):** Outlines how DSPy could be used to optimize the prompts and few-shot examples provided to the LLM, enhancing its performance over time.
*   **Evaluation Frameworks (Conceptual):** Mentions the future possibility of using frameworks like `deepeval` or `ragas` to evaluate the generated test scripts and drive a closed-loop improvement mechanism.

This project, in its current state, is a **Proof of Concept** to demonstrate the foundational workflow and component interactions.

## 2. Features (PoC Level)

*   **Natural Language Input:** Takes a natural language description of a test case (simulated processing).
*   **RAG System:** Retrieves relevant examples from a small, predefined dataset using a basic keyword-matching RAG system (`src/rag_system.py`).
*   **Pytest Script Generation:** Generates Pytest scripts (currently using a hardcoded LLM response via `src/llm_interface.py`) that utilize a custom, dummy test API (`src/custom_test_api.py`).
*   **Script Saving:** Saves the generated Pytest scripts to the `generated_tests/` directory.
*   **Script Evaluation:** Evaluates the generated scripts using a placeholder evaluation mechanism (`src/evaluator.py`) that provides a dummy score and feedback.
*   **Conceptual DSPy Integration:** Outlines how DSPy could be integrated for future optimization of the generation process (`src/dspy_optimizer.py`).
*   **End-to-End Workflow:** Demonstrates the complete, albeit simulated, workflow from natural language input to script generation and evaluation via `main.py`.

## 3. Directory Structure

*   `src/`: Contains all core source code for the PoC components.
    *   `custom_test_api.py`: Dummy API for test scripts.
    *   `dspy_optimizer.py`: Conceptual outline for DSPy integration.
    *   `evaluator.py`: Placeholder for script evaluation.
    *   `llm_interface.py`: Simulated LLM interface for script generation.
    *   `rag_system.py`: Basic RAG implementation.
*   `data_for_rag/`: Contains sample text files with natural language test cases and their ideal Pytest script implementations, used by the RAG system.
*   `generated_tests/`: The output directory where generated Pytest scripts are saved.
*   `main.py`: The main script to run the end-to-end PoC workflow.
*   `README.md`: This file, providing information about the project.
*   `.gitkeep`: Placeholder files to ensure empty directories are tracked by Git.

## 4. Setup and Installation

Conceptually, a full version of this project would require:
*   Python 3.x
*   `pytest` (for running generated tests)
*   `dspy-ai` (for DSPy optimization)
*   `ragas` / `deepeval` (for advanced script evaluation and feedback)
*   A vector database (e.g., `faiss-cpu`, `chromadb`) for a more sophisticated RAG system.
*   An LLM client library (e.g., `openai`, `langchain`).

**For this Proof of Concept:**
*   The core logic runs with standard Python libraries.
*   LLM interactions and DSPy optimization are simulated and do not require external libraries or API keys.
*   You primarily need Python 3.x to run `main.py`.

While not strictly enforced for this PoC, a typical project would use a `requirements.txt` file:
```bash
# pip install -r requirements.txt
```

## 5. How to Run

1.  Ensure you have Python 3 installed.
2.  Clone the repository (if applicable).
3.  Navigate to the root directory of the project.
4.  Run the main script:
    ```bash
    python main.py
    ```
The script will print output to the console, walking through each step of the PoC workflow:
*   The sample natural language test case.
*   RAG system loading and retrieving examples.
*   The constructed prompt for the (simulated) LLM.
*   The (hardcoded) generated Pytest script.
*   Confirmation of the script being saved.
*   The dummy evaluation results.
*   Messages from the conceptual DSPy module demonstration.

## 6. Components Explained

*   **Test Case Input:**
    The system starts with a natural language string describing the test case (defined in `main.py`).

*   **RAG System (`src/rag_system.py`):**
    *   `load_rag_data()`: Reads `.txt` files from `data_for_rag/`. Each file is expected to contain a natural language test case and its corresponding ideal Pytest script.
    *   `retrieve_relevant_examples()`: Given a new natural language query, it attempts to find the most relevant stored example. In this PoC, it uses a simple heuristic (checking for "invalid" in the query/filename) and basic keyword matching between the query and the stored natural language cases.

*   **LLM Interface (`src/llm_interface.py`):**
    *   `generate_test_script()`: This function simulates an LLM call. Currently, it **returns a hardcoded Pytest script** regardless of the prompt. It also prints the prompt it received. This is a placeholder for a real LLM integration.

*   **Custom Test API (`src/custom_test_api.py`):**
    *   Provides a set of dummy Python functions (e.g., `navigate_to_url`, `click_element`, `input_text`, `verify_text`) that the generated Pytest scripts will use. These functions print simulation messages rather than interacting with a real UI.

*   **Evaluation (`src/evaluator.py`):**
    *   `evaluate_script()`: A placeholder for a more sophisticated script evaluation system. It performs very basic checks (e.g., presence of `import pytest`, `def test_`) and returns a randomly generated score and textual feedback.

*   **DSPy Optimizer (`src/dspy_optimizer.py`):**
    *   This file provides a **conceptual outline** of how DSPy could be integrated. It includes a `ConceptualTestGenerationModule` and a `conceptual_dspy_optimization_loop` function that use print statements to describe how DSPy's components (Signatures, Modules, Teleprompters, Metrics) would be used to refine prompts and few-shot examples for the LLM. No actual DSPy code is executed.

## 7. Closed-Loop Improvement Mechanism (Concept)

The long-term vision for this system involves a continuous improvement loop:

1.  **Generate:** The LLM, informed by the RAG system, generates a Pytest script for a given natural language test case.
2.  **Execute:** The generated script is executed against the Application Under Test (AUT).
3.  **Evaluate:**
    *   The script's execution results (pass/fail, errors) are collected.
    *   Frameworks like `deepeval` or `ragas` could be used to analyze the script's quality, correctness, and coverage against the original intent.
    *   Other metrics like code quality or adherence to best practices could also be incorporated.
4.  **Collect Feedback:** All evaluation data and execution results are collected and structured.
5.  **Optimize (DSPy):** A framework like DSPy is used to analyze this feedback.
    *   **Teleprompters** in DSPy can automatically refine the prompts sent to the LLM.
    *   They can also select better few-shot examples for the RAG system from a larger pool of successful (or even corrected unsuccessful) test scripts.
    *   Over time, this can lead to LLM fine-tuning or the development of more specialized models.
6.  **Iterate:** This cycle of generation, execution, evaluation, and optimization continuously improves the quality and reliability of the generated test scripts.

## 8. Limitations of PoC

*   **Simulated LLM:** The LLM's response is hardcoded in `src/llm_interface.py`. No actual natural language processing or generation by an LLM occurs.
*   **Conceptual DSPy:** DSPy integration is purely conceptual, described through comments and print statements in `src/dspy_optimizer.py`. No DSPy optimization is performed.
*   **Basic RAG:** The RAG system (`src/rag_system.py`) uses simple keyword matching, not advanced techniques like vector embeddings or semantic search. The dataset is also very small.
*   **Placeholder Evaluation:** The script evaluation (`src/evaluator.py`) is a placeholder and does not reflect true script quality or correctness.
*   **No Actual Test Execution:** Generated tests are not executed against any real application. The custom test API (`src/custom_test_api.py`) only simulates actions.
*   **Limited Error Handling:** The PoC has minimal error handling.

## 9. Future Work/Potential Enhancements

*   **Integrate a Real LLM:** Replace the hardcoded script generation with calls to an actual LLM (e.g., via OpenAI API, Hugging Face models).
*   **Implement Full DSPy Optimization:** Develop and run DSPy programs with teleprompters and metrics to optimize prompts and few-shot examples.
*   **Sophisticated RAG System:** Implement a RAG system using vector embeddings (e.g., Sentence Transformers) and a vector database (e.g., FAISS, ChromaDB) for more accurate retrieval.
*   **Advanced Evaluation:** Integrate frameworks like `deepeval` or `ragas` to evaluate generated scripts based on their execution against a real AUT and their alignment with the original test case.
*   **Connect to a Real AUT:** Develop the custom test API to interact with a real web application or other software.
*   **Fine-Tuning:** Explore fine-tuning smaller, specialized LLMs for the task of test script generation.
*   **User Interface:** Create a simple UI (e.g., using Streamlit or Flask) for easier input of natural language test cases and management of generated scripts.
*   **Expanded Test Coverage:** Support for a wider range of Pytest features and testing scenarios.
*   **Robust Error Handling and Logging.**
```
