import pytest

from backend.application.errors import InvalidPhoneNumberError
from backend.application.validators.phone import normalize_ukraine_phone


class TestNormalizeUkrainePhone:
    def test_already_correct_format(self):
        assert normalize_ukraine_phone("+380980074978") == "+380980074978"

    def test_with_380_prefix(self):
        assert normalize_ukraine_phone("380980074978") == "+380980074978"

    def test_with_leading_zero(self):
        assert normalize_ukraine_phone("0980074978") == "+380980074978"

    def test_without_country_code(self):
        assert normalize_ukraine_phone("980074978") == "+380980074978"

    def test_with_spaces(self):
        assert normalize_ukraine_phone("+38 098 007 49 78") == "+380980074978"
        assert normalize_ukraine_phone("098 007 49 78") == "+380980074978"

    def test_with_dashes(self):
        assert normalize_ukraine_phone("+380-98-007-49-78") == "+380980074978"
        assert normalize_ukraine_phone("098-007-49-78") == "+380980074978"

    def test_with_parentheses(self):
        assert normalize_ukraine_phone("+38(098)007-49-78") == "+380980074978"
        assert normalize_ukraine_phone("(098)007-49-78") == "+380980074978"

    def test_with_mixed_formatting(self):
        assert (
            normalize_ukraine_phone("+38 (098) 007-49-78") == "+380980074978"
        )
        assert normalize_ukraine_phone("0(98)007 49 78") == "+380980074978"

    def test_different_operators(self):
        assert normalize_ukraine_phone("0501234567") == "+380501234567"
        assert normalize_ukraine_phone("0671234567") == "+380671234567"
        assert normalize_ukraine_phone("0931234567") == "+380931234567"

    def test_invalid_too_short(self):
        with pytest.raises(InvalidPhoneNumberError) as exc_info:
            normalize_ukraine_phone("098007497")
        assert "098007497" in exc_info.value.message
        assert "9 digits" in exc_info.value.message

    def test_invalid_too_long(self):
        with pytest.raises(InvalidPhoneNumberError) as exc_info:
            normalize_ukraine_phone("09800749781234")
        assert "09800749781234" in exc_info.value.message
        assert "9 digits" in exc_info.value.message

    def test_invalid_non_digits_after_code(self):
        with pytest.raises(InvalidPhoneNumberError):
            normalize_ukraine_phone("+380abc007497")

    def test_various_real_formats(self):
        test_cases = [
            ("+380980074978", "+380980074978"),
            ("380980074978", "+380980074978"),
            ("0980074978", "+380980074978"),
            ("980074978", "+380980074978"),
            ("+38 098 007 49 78", "+380980074978"),
            ("+38-098-007-49-78", "+380980074978"),
            ("+38(098)007-49-78", "+380980074978"),
            ("(098) 007-49-78", "+380980074978"),
            ("098 007 49 78", "+380980074978"),
        ]

        for input_phone, expected in test_cases:
            assert normalize_ukraine_phone(input_phone) == expected
