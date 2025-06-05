# AI 驱动的测试用例到 Pytest 脚本生成概念验证

## 1. 概述/目的

本项目的目标是构建一个概念验证（PoC）系统，利用大语言模型（LLM）来理解自然语言测试用例，并自动生成相应的 Pytest 自动化测试脚本。

这个 PoC 探索了以下几个关键概念的集成：
*   **检索增强生成（RAG）：** 为 LLM 提供相关上下文和示例，提高生成脚本的质量和相关性。
*   **DSPy 优化（概念性）：** 概述了如何使用 DSPy 来优化提供给 LLM 的提示和少量示例，随着时间的推移提高其性能。
*   **评估框架（概念性）：** 提到未来可能使用 `deepeval` 或 `ragas` 等框架来评估生成的测试脚本，并推动闭环改进机制。

目前，这个项目是一个**概念验证**，用于展示基础工作流程和组件交互。

## 2. 功能（PoC 级别）

*   **自然语言输入：** 接收测试用例的自然语言描述（模拟处理）。
*   **RAG 系统：** 使用基本的关键词匹配 RAG 系统（`src/rag_system.py`）从预定义的小型数据集中检索相关示例。
*   **Pytest 脚本生成：** 生成 Pytest 脚本（目前使用 `src/llm_interface.py` 中的硬编码 LLM 响应），这些脚本使用自定义的模拟测试 API（`src/custom_test_api.py`）。
*   **脚本保存：** 将生成的 Pytest 脚本保存到 `generated_tests/` 目录。
*   **脚本评估：** 使用占位评估机制（`src/evaluator.py`）评估生成的脚本，提供模拟分数和反馈。
*   **概念性 DSPy 集成：** 概述了如何集成 DSPy 以优化未来的生成过程（`src/dspy_optimizer.py`）。
*   **端到端工作流：** 通过 `main.py` 演示从自然语言输入到脚本生成和评估的完整（虽然是模拟的）工作流程。

## 3. 目录结构

*   `src/`: 包含 PoC 组件的所有核心源代码。
    *   `custom_test_api.py`: 测试脚本的模拟 API。
    *   `dspy_optimizer.py`: DSPy 集成的概念性概述。
    *   `evaluator.py`: 脚本评估的占位符。
    *   `llm_interface.py`: 脚本生成的模拟 LLM 接口。
    *   `rag_system.py`: 基础 RAG 实现。
*   `data_for_rag/`: 包含自然语言测试用例及其理想 Pytest 脚本实现的示例文本文件，供 RAG 系统使用。
*   `generated_tests/`: 保存生成的 Pytest 脚本的输出目录。
*   `main.py`: 运行端到端 PoC 工作流的主脚本。
*   `README.md`: 本文件，提供项目信息。
*   `.gitkeep`: 确保空目录被 Git 跟踪的占位文件。

## 4. 设置和安装

从概念上讲，完整版本的项目需要：
*   Python 3.x
*   `pytest`（用于运行生成的测试）
*   `dspy-ai`（用于 DSPy 优化）
*   `ragas` / `deepeval`（用于高级脚本评估和反馈）
*   向量数据库（如 `faiss-cpu`、`chromadb`）用于更复杂的 RAG 系统。
*   LLM 客户端库（如 `openai`、`langchain`）。

**对于这个概念验证：**
*   核心逻辑使用标准 Python 库运行。
*   LLM 交互和 DSPy 优化是模拟的，不需要外部库或 API 密钥。
*   您主要需要 Python 3.x 来运行 `main.py`。

虽然这个 PoC 没有严格强制执行，但典型项目会使用 `requirements.txt` 文件：
```bash
# pip install -r requirements.txt
```

## 5. 如何运行

1.  确保已安装 Python 3。
2.  克隆仓库（如果适用）。
3.  导航到项目的根目录。
4.  运行主脚本：
    ```bash
    python main.py
    ```
脚本将打印输出到控制台，展示 PoC 工作流程的每个步骤：
*   示例自然语言测试用例。
*   RAG 系统加载和检索示例。
*   为（模拟的）LLM 构建的提示。
*   （硬编码的）生成的 Pytest 脚本。
*   脚本保存确认。
*   模拟评估结果。
*   概念性 DSPy 模块演示的消息。

## 6. 组件说明

*   **测试用例输入：**
    系统从描述测试用例的自然语言字符串开始（在 `main.py` 中定义）。

*   **RAG 系统（`src/rag_system.py`）：**
    *   `load_rag_data()`: 从 `data_for_rag/` 读取 `.txt` 文件。每个文件应包含一个自然语言测试用例及其相应的理想 Pytest 脚本。
    *   `retrieve_relevant_examples()`: 给定一个新的自然语言查询，它尝试找到最相关的存储示例。在这个 PoC 中，它使用简单的启发式方法（检查查询/文件名中的"invalid"）和查询与存储的自然语言用例之间的基本关键词匹配。

*   **LLM 接口（`src/llm_interface.py`）：**
    *   `generate_test_script()`: 此函数模拟 LLM 调用。目前，它**返回一个硬编码的 Pytest 脚本**，不管提示是什么。它还打印收到的提示。这是真实 LLM 集成的占位符。

*   **自定义测试 API（`src/custom_test_api.py`）：**
    *   提供一组模拟的 Python 函数（如 `navigate_to_url`、`click_element`、`input_text`、`verify_text`），生成的 Pytest 脚本将使用这些函数。这些函数打印模拟消息，而不是与真实 UI 交互。

*   **评估（`src/evaluator.py`）：**
    *   `evaluate_script()`: 更复杂的脚本评估系统的占位符。它执行非常基本的检查（如存在 `import pytest`、`def test_`）并返回随机生成的分数和文本反馈。

*   **DSPy 优化器（`src/dspy_optimizer.py`）：**
    *   此文件提供了如何集成 DSPy 的**概念性概述**。它包括一个 `ConceptualTestGenerationModule` 和一个 `conceptual_dspy_optimization_loop` 函数，使用打印语句描述如何使用 DSPy 的组件（Signatures、Modules、Teleprompters、Metrics）来优化提供给 LLM 的提示和少量示例。没有执行实际的 DSPy 代码。

## 7. 闭环改进机制（概念）

该系统的长期愿景涉及一个持续改进循环：

1.  **生成：** LLM 在 RAG 系统的指导下，为给定的自然语言测试用例生成 Pytest 脚本。
2.  **执行：** 生成的脚本针对被测应用（AUT）执行。
3.  **评估：**
    *   收集脚本的执行结果（通过/失败、错误）。
    *   可以使用 `deepeval` 或 `ragas` 等框架来分析脚本的质量、正确性和与原始意图的覆盖度。
    *   还可以纳入其他指标，如代码质量或对最佳实践的遵守。
4.  **收集反馈：** 收集并结构化所有评估数据和执行结果。
5.  **优化（DSPy）：** 使用 DSPy 等框架分析这些反馈。
    *   DSPy 中的**Teleprompters**可以自动优化发送给 LLM 的提示。
    *   它们还可以从更大的成功（或甚至修正的不成功）测试脚本池中为 RAG 系统选择更好的少量示例。
    *   随着时间的推移，这可能导致 LLM 微调或开发更专门的模型。
6.  **迭代：** 这个生成、执行、评估和优化的循环不断改进生成的测试脚本的质量和可靠性。

## 8. PoC 的限制

*   **模拟 LLM：** LLM 的响应在 `src/llm_interface.py` 中是硬编码的。没有发生实际的 LLM 自然语言处理或生成。
*   **概念性 DSPy：** DSPy 集成纯粹是概念性的，通过 `src/dspy_optimizer.py` 中的注释和打印语句描述。没有执行 DSPy 优化。
*   **基础 RAG：** RAG 系统（`src/rag_system.py`）使用简单的关键词匹配，而不是向量嵌入或语义搜索等高级技术。数据集也很小。
*   **占位符评估：** 脚本评估（`src/evaluator.py`）是一个占位符，不反映真实的脚本质量或正确性。
*   **没有实际测试执行：** 生成的测试不会针对任何真实应用执行。自定义测试 API（`src/custom_test_api.py`）只模拟操作。
*   **有限的错误处理：** PoC 只有最小的错误处理。

## 9. 未来工作/潜在增强

*   **集成真实 LLM：** 用对实际 LLM 的调用（如通过 OpenAI API、Hugging Face 模型）替换硬编码的脚本生成。
*   **实现完整 DSPy 优化：** 开发和运行带有 teleprompters 和指标的 DSPy 程序，以优化提示和少量示例。
*   **复杂的 RAG 系统：** 使用向量嵌入（如 Sentence Transformers）和向量数据库（如 FAISS、ChromaDB）实现 RAG 系统，以获得更准确的检索。
*   **高级评估：** 集成 `deepeval` 或 `ragas` 等框架，根据脚本对真实 AUT 的执行情况和与原始测试用例的一致性来评估生成的脚本。
*   **连接到真实 AUT：** 开发自定义测试 API 以与真实 Web 应用程序或其他软件交互。
*   **微调：** 探索为测试脚本生成任务微调较小的专业 LLM。
*   **用户界面：** 创建简单的 UI（如使用 Streamlit 或 Flask）以便更容易输入自然语言测试用例和管理生成的脚本。
*   **扩展测试覆盖：** 支持更广泛的 Pytest 功能和测试场景。
*   **健壮的错误处理和日志记录。**
```
