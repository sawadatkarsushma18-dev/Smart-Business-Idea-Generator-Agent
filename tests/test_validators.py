"""
tests/test_validators.py – Unit tests for input validation helpers.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.validators import (
    validate_budget,
    validate_text_field,
    sanitize_input,
    validate_profile,
)


class TestValidateBudget:
    def test_plain_number(self):
        ok, _ = validate_budget("5000")
        assert ok

    def test_dollar_sign(self):
        ok, _ = validate_budget("$5000")
        assert ok

    def test_rupee_with_unit(self):
        ok, _ = validate_budget("50000 INR")
        assert ok

    def test_k_suffix(self):
        ok, _ = validate_budget("10k")
        assert ok

    def test_free_text(self):
        ok, _ = validate_budget("Bootstrap / Zero budget")
        assert ok

    def test_empty_fails(self):
        ok, msg = validate_budget("")
        assert not ok
        assert "empty" in msg.lower()


class TestValidateTextField:
    def test_valid_field(self):
        ok, _ = validate_text_field("Python developer", "Skills")
        assert ok

    def test_too_short(self):
        ok, msg = validate_text_field("AB", "Skills", min_len=3)
        assert not ok
        assert "3" in msg

    def test_empty(self):
        ok, _ = validate_text_field("", "Interest")
        assert not ok


class TestSanitizeInput:
    def test_removes_angle_brackets(self):
        result = sanitize_input("<script>alert('x')</script>")
        assert "<" not in result
        assert ">" not in result

    def test_removes_backtick(self):
        result = sanitize_input("hello `world`")
        assert "`" not in result

    def test_collapses_whitespace(self):
        result = sanitize_input("hello    world   test")
        assert "   " not in result

    def test_strips_leading_trailing(self):
        result = sanitize_input("   hello   ")
        assert result == "hello"


class TestValidateProfile:
    def _base_profile(self):
        return {
            "interest": "EdTech",
            "skills": "Python, Teaching",
            "budget": "$5000",
            "country": "India",
            "target_audience": "College students",
        }

    def test_valid_profile(self):
        ok, errors = validate_profile(self._base_profile())
        assert ok
        assert errors == []

    def test_missing_interest(self):
        p = self._base_profile()
        p["interest"] = ""
        ok, errors = validate_profile(p)
        assert not ok
        assert len(errors) > 0

    def test_missing_budget(self):
        p = self._base_profile()
        p["budget"] = ""
        ok, errors = validate_profile(p)
        assert not ok

    def test_multiple_errors(self):
        p = {
            "interest": "",
            "skills": "",
            "budget": "",
            "country": "",
            "target_audience": "",
        }
        ok, errors = validate_profile(p)
        assert not ok
        assert len(errors) >= 3
