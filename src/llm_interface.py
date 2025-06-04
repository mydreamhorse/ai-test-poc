import os
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

def clean_generated_script(script: str) -> str:
    """
    清理生成的脚本，移除Markdown代码块标记和其他不必要的字符。

    Args:
        script: 原始生成的脚本。

    Returns:
        清理后的脚本。
    """
    # 移除Markdown代码块标记
    script = script.replace("```python", "").replace("```", "")
    
    # 移除开头的空行
    script = script.lstrip()
    
    # 确保脚本以import语句开始
    if not script.startswith("import"):
        script = "import pytest\nfrom src.custom_test_api import *\n\n" + script
    
    return script

def generate_test_script(prompt: str, api_key: Optional[str] = None) -> str:
    """
    Generates a Pytest script based on a given prompt using OpenAI's API.

    Args:
        prompt: The input prompt describing the test case.
        api_key: Optional OpenAI API key. If not provided, will try to use OPENAI_API_KEY from .env file.

    Returns:
        A string containing the generated Pytest script.
    """
    print(f"Received prompt: {prompt}")

    # 设置API密钥
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is required. Please provide it as an argument or set OPENAI_API_KEY in .env file.")

    # 初始化OpenAI客户端
    client = OpenAI(api_key=api_key)

    try:
        # 构建系统提示
        system_prompt = """You are an expert test automation engineer. Your task is to generate Pytest test scripts based on natural language test cases.
        The scripts should use the following custom_test_api functions for UI interactions:
        - setup_test_environment(): Sets up the test environment
        - teardown_test_environment(): Tears down the test environment
        - navigate_to_url(url: str): Navigates to a URL
        - click_element(element_id: str): Clicks a UI element
        - input_text(element_id: str, text_to_input: str): Inputs text into a UI element
        - verify_text(element_id: str, expected_text: str): Verifies text of a UI element
        - verify_element_exists(element_id: str): Verifies that a UI element exists

        Always include proper setup and teardown.
        Follow Pytest best practices and include appropriate assertions.
        Do not include any markdown formatting or code block markers in your response.
        Do not use any functions that are not listed above.
        For form submission, use click_element() on the submit button instead of a non-existent submit_form() function."""

        # 调用OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # 提取生成的脚本并清理
        generated_script = response.choices[0].message.content.strip()
        generated_script = clean_generated_script(generated_script)

        return generated_script

    except Exception as e:
        print(f"Error generating test script: {str(e)}")
        # 在发生错误时返回一个基本的测试脚本
        return """
import pytest
from src.custom_test_api import *

def test_basic_functionality():
    setup_test_environment()
    # Basic test steps
    teardown_test_environment()
"""

if __name__ == '__main__':
    # 示例用法（可选，用于本地测试）
    sample_prompt = "Test case: Successful login and dashboard verification."
    try:
        generated_script = generate_test_script(sample_prompt)
        print("\n--- Generated Script ---")
        print(generated_script)
        print("------------------------\n")
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please set your OpenAI API key in .env file.")
