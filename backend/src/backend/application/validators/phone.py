import re

from backend.application.errors import InvalidPhoneNumberError


def normalize_ukraine_phone(phone: str) -> str:
    """Normalize Ukrainian phone number to +380 format.

    Examples:
        +380980074978 -> +380980074978 (already correct)
        380980074978  -> +380980074978 (add +)
        0980074978    -> +380980074978 (replace 0 with +380)
        980074978     -> +380980074978 (add +380)
        +38 098 007 49 78 -> +380980074978 (remove spaces)
        +38(098)007-49-78 -> +380980074978 (remove formatting)
    """
    # Remove all non-digit characters except leading +
    cleaned = re.sub(r"[^\d+]", "", phone)

    # Remove + from the middle or end (keep only leading +)
    if cleaned.startswith("+"):
        cleaned = "+" + cleaned[1:].replace("+", "")
    else:
        cleaned = cleaned.replace("+", "")

    # Normalize to +380 format
    if cleaned.startswith("+380"):
        # Already in correct format
        normalized = cleaned
    elif cleaned.startswith("380"):
        # Add + prefix
        normalized = "+" + cleaned
    elif cleaned.startswith("0"):
        # Replace leading 0 with +380
        normalized = "+380" + cleaned[1:]
    else:
        # Assume it's a local number without country code
        normalized = "+380" + cleaned

    if len(normalized) != 13:
        raise InvalidPhoneNumberError(
            phone=phone,
            reason=(
                f"Expected format: +380XXXXXXXXX (9 digits after +380), "
                f"got {len(normalized) - 4} digits"
            ),
        )

    if not normalized[4:].isdigit():
        raise InvalidPhoneNumberError(
            phone=phone,
            reason="Must contain only digits after country code +380",
        )

    return normalized
