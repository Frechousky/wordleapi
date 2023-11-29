import os
from unittest.mock import Mock, patch

import pytest

from wordleapi.core import load_whitelist_file


def test_load_whitelist_file__success():
    assert load_whitelist_file(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data", "whitelist_6_fr.txt"
        )
    ) == (
        "abacas",
        "abales",
        "abaque",
        "abasie",
        "abatee",
        "abatis",
        "abatte",
        "abattu",
    )


@patch("wordleapi.core.open")
def test_load_whitelist_file__open_raises_exception__raises_exception(mock_open: Mock):
    mock_open.side_effect = OSError

    with pytest.raises(OSError):
        load_whitelist_file("whitelist_6_fr.txt")
