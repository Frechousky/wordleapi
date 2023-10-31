import os
from unittest.mock import Mock, patch

import pytest

from wordleapi.core import load_wordlefile


def test_load_wordlefile__success():
    assert load_wordlefile(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data", "wordle_6_fr.txt"
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
def test_load_wordlefile__open_raises_exception__raises_exception(mock_open: Mock):
    mock_open.side_effect = OSError

    with pytest.raises(OSError):
        load_wordlefile("wordle_6_fr.txt")
