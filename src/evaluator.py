import random
import re
from typing import Dict, List, Tuple

def check_pytest_import(script_content: str) -> Tuple[bool, str]:
    """
    检查脚本是否包含pytest导入。
    
    Args:
        script_content: 脚本内容
        
    Returns:
        (是否通过, 反馈信息)
    """
    if "import pytest" in script_content:
        return True, "包含pytest导入"
    return False, "缺少pytest导入"

def check_test_function(script_content: str) -> Tuple[bool, str]:
    """
    检查脚本是否包含测试函数定义。
    
    Args:
        script_content: 脚本内容
        
    Returns:
        (是否通过, 反馈信息)
    """
    if re.search(r"def\s+test_", script_content):
        return True, "包含测试函数定义"
    return False, "缺少测试函数定义"

def check_setup_teardown(script_content: str) -> Tuple[bool, str]:
    """
    检查脚本是否包含setup和teardown。
    
    Args:
        script_content: 脚本内容
        
    Returns:
        (是否通过, 反馈信息)
    """
    has_setup = "setup_test_environment()" in script_content
    has_teardown = "teardown_test_environment()" in script_content
    
    if has_setup and has_teardown:
        return True, "包含完整的测试环境设置和清理"
    elif has_setup:
        return False, "缺少测试环境清理"
    elif has_teardown:
        return False, "缺少测试环境设置"
    return False, "缺少测试环境设置和清理"

def check_api_functions(script_content: str) -> Tuple[float, List[str]]:
    """
    检查脚本中API函数的使用情况。
    
    Args:
        script_content: 脚本内容
        
    Returns:
        (得分, 反馈信息列表)
    """
    required_functions = {
        'navigate_to_url': '导航到URL',
        'input_text': '输入文本',
        'click_element': '点击元素',
        'verify_text': '验证文本',
        'verify_element_exists': '验证元素存在'
    }
    
    feedback = []
    score = 0.0
    
    for func, desc in required_functions.items():
        if func in script_content:
            score += 0.2  # 每个函数0.2分
        else:
            feedback.append(f"缺少{desc}函数")
    
    return min(score, 1.0), feedback

def check_test_steps(script_content: str, test_case_description: str) -> Tuple[float, List[str]]:
    """
    检查测试步骤的完整性。
    
    Args:
        script_content: 脚本内容
        test_case_description: 测试用例描述
        
    Returns:
        (得分, 反馈信息列表)
    """
    # 从测试用例描述中提取关键步骤
    steps = []
    if "register" in test_case_description.lower():
        steps.extend(["navigate_to_url", "input_text", "click_element"])
    if "login" in test_case_description.lower():
        steps.extend(["navigate_to_url", "input_text", "click_element"])
    if "verify" in test_case_description.lower():
        steps.extend(["verify_text", "verify_element_exists"])
    
    # 去重
    steps = list(set(steps))
    
    # 检查每个步骤是否在脚本中
    missing_steps = []
    for step in steps:
        if step not in script_content:
            missing_steps.append(step)
    
    # 计算得分
    if not steps:  # 如果没有可识别的步骤
        return 0.5, ["无法从测试用例描述中识别具体步骤"]
    
    score = (len(steps) - len(missing_steps)) / len(steps)
    feedback = [f"缺少步骤: {step}" for step in missing_steps]
    
    return score, feedback

def evaluate_script(script_content: str, test_case_description: str = "") -> dict:
    """
    评估生成的Pytest脚本。

    Args:
        script_content: 脚本内容
        test_case_description: 测试用例描述

    Returns:
        包含评分、反馈和通过检查的字典
    """
    print(f"Performing evaluation for script (first 100 chars): '{script_content[:100]}...'")
    if test_case_description:
        print(f"With test case description: '{test_case_description}'")

    # 执行各项检查
    pytest_import_result = check_pytest_import(script_content)
    test_function_result = check_test_function(script_content)
    setup_teardown_result = check_setup_teardown(script_content)
    api_functions_score, api_feedback = check_api_functions(script_content)
    test_steps_score, steps_feedback = check_test_steps(script_content, test_case_description)

    # 收集所有通过的检查
    passed_checks = []
    if pytest_import_result[0]:
        passed_checks.append('pytest_import_found')
    if test_function_result[0]:
        passed_checks.append('test_function_defined')
    if setup_teardown_result[0]:
        passed_checks.append('setup_teardown_complete')

    # 计算总分
    # 基础检查（pytest导入和测试函数）占40%
    # API函数使用占30%
    # 测试步骤完整性占30%
    base_score = 0.4 * (pytest_import_result[0] + test_function_result[0]) / 2
    total_score = base_score + 0.3 * api_functions_score + 0.3 * test_steps_score

    # 收集所有反馈
    feedback_parts = []
    if not pytest_import_result[0]:
        feedback_parts.append(pytest_import_result[1])
    if not test_function_result[0]:
        feedback_parts.append(test_function_result[1])
    if not setup_teardown_result[0]:
        feedback_parts.append(setup_teardown_result[1])
    feedback_parts.extend(api_feedback)
    feedback_parts.extend(steps_feedback)

    # 生成最终反馈
    if total_score >= 0.9:
        feedback = "脚本质量优秀，包含了所有必要的元素。"
    elif total_score >= 0.7:
        feedback = "脚本质量良好，但有一些需要改进的地方。"
    elif total_score >= 0.5:
        feedback = "脚本基本可用，但需要较多改进。"
    else:
        feedback = "脚本需要重大改进。"

    if feedback_parts:
        feedback += " 具体问题：" + "；".join(feedback_parts)

    return {
        'score': round(total_score, 2),
        'feedback': feedback,
        'passed_checks': passed_checks,
        'detailed_feedback': {
            'pytest_import': pytest_import_result,
            'test_function': test_function_result,
            'setup_teardown': setup_teardown_result,
            'api_functions': {'score': api_functions_score, 'feedback': api_feedback},
            'test_steps': {'score': test_steps_score, 'feedback': steps_feedback}
        }
    }

if __name__ == '__main__':
    # 测试用例
    sample_valid_script = """
import pytest
from src.custom_test_api import *

def test_example_case():
    setup_test_environment()
    navigate_to_url("https://example.com")
    input_text("username", "test_user")
    input_text("password", "test_pass")
    click_element("login_button")
    verify_element_exists("dashboard")
    verify_text("welcome_message", "Welcome, test_user!")
    teardown_test_environment()
"""
    sample_invalid_script = """
def test_missing_import():
    print("This will not run with pytest easily")
"""

    print("--- Evaluating Valid Script ---")
    eval_result1 = evaluate_script(sample_valid_script, "Test user login and verify welcome message")
    print(f"Evaluation Result: {eval_result1}\n")

    print("--- Evaluating Invalid Script ---")
    eval_result2 = evaluate_script(sample_invalid_script)
    print(f"Evaluation Result: {eval_result2}\n")
