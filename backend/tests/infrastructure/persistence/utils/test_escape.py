import pytest

from backend.infrastructure.persistence.utils.escape import escape_like


@pytest.mark.parametrize(
    ("input_value", "expected"),
    (
        ("hello", "hello"),
        ("100%", "100\\%"),
        ("file_name", "file\\_name"),
        ("%admin%", "\\%admin\\%"),
        ("__init__", "\\_\\_init\\_\\_"),
        ("back\\slash", "back\\\\slash"),
        ("%_\\", "\\%\\_\\\\"),
        ("", ""),
    ),
)
def test_escape_like(input_value: str, expected: str) -> None:
    assert escape_like(input_value) == expected
