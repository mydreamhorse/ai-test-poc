
import pytest
from src.custom_test_api import *

def test_login_and_verify_dashboard():
    setup_test_environment()
    navigate_to_url("https://example.com/login")
    input_text("username_field", "testuser")
    input_text("password_field", "password123")
    click_element("login_button")
    verify_element_exists("dashboard_header")
    verify_text("welcome_message", "Welcome, testuser!")
    teardown_test_environment()
