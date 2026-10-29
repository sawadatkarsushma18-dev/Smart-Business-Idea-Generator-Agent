"""
utils/validators.py – Input validation helpers for the user profile form.
"""

import re
from typing import Tuple


def validate_budget(budget_str: str) -> Tuple[bool, str]:
    """
    Accept budgets like '$500', '1000 USD', '50000 INR', '10k', or plain numbers.
    Returns (is_valid, message).
    """
    if not budget_str.strip():
        return False, "Budget cannot be empty."
    # Allow alphanumeric with common currency symbols and 'k'/'m'
    pattern = r"^[\$€£₹]?\s*[\d,]+\.?\d*\s*[kKmMbB]?\s*(USD|INR|EUR|GBP|AUD)?$"
    cleaned = budget_str.strip()
    if re.match(pattern, cleaned, re.IGNORECASE):
        return True, ""
    # Allow free-form text like "Under $5000" or "Bootstrap / Zero"
    if len(cleaned) <= 80:
        return True, ""
    return False, "Please enter a valid budget (e.g. '$5000', '10k INR', 'Bootstrap')."


def validate_text_field(value: str, field_name: str, min_len: int = 3) -> Tuple[bool, str]:
    """Generic non-empty text field validator."""
    if not value or len(value.strip()) < min_len:
        return False, f"'{field_name}' must be at least {min_len} characters long."
    return True, ""


def sanitize_input(text: str) -> str:
    """
    Remove characters that could be used for prompt injection.
    Strips leading/trailing whitespace and collapses internal whitespace.
    """
    # Remove characters commonly used for prompt injection attempts
    text = re.sub(r"[<>{}|\\^`]", "", text)
    # Collapse multiple whitespace
    text = re.sub(r"\s{3,}", " ", text).strip()
    return text


def validate_profile(profile_data: dict) -> Tuple[bool, list]:
    """
    Validate the full user profile dict.
    Returns (all_valid, list_of_error_messages).
    """
    errors = []
    required_fields = {
        "interest": "Area of Interest",
        "skills": "Skills",
        "budget": "Budget",
        "country": "Country",
        "target_audience": "Target Audience",
    }
    for key, label in required_fields.items():
        val = profile_data.get(key, "")
        if key == "budget":
            ok, msg = validate_budget(val)
        else:
            ok, msg = validate_text_field(val, label)
        if not ok:
            errors.append(msg)

    return len(errors) == 0, errors
