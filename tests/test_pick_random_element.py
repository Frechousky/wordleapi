from unittest.mock import patch, Mock

import pytest

from wordleapi.utils import pick_random_element


@pytest.mark.parametrize(
    "seq",
    (
        [
            "abacas",
            "abales",
            "abaque",
            "abasie",
            "abatee",
            "abatis",
            "abatte",
            "abattu",
            "abbaye",
            "abceda",
            "abcede",
            "abelia",
            "abelie",
            "aberra",
            "aberre",
            "abetie",
            "abetir",
            "abetis",
            "abetit",
            "abimai",
        ],
    ),
)
def test_pick_random_element(seq: list):
    for i in range(1000):
        ret = pick_random_element(seq)
        assert ret in seq, "element should be in sequence"


@pytest.mark.parametrize(
    "seq",
    (
        [
            "abacas",
            "abales",
            "abaque",
            "abasie",
            "abatee",
            "abatis",
            "abatte",
            "abattu",
            "abbaye",
            "abceda",
            "abcede",
            "abelia",
            "abelie",
            "aberra",
            "aberre",
            "abetie",
            "abetir",
            "abetis",
            "abetit",
            "abimai",
        ],
    ),
)
@patch("wordleapi.utils.random")
def test_pick_random_element__seed_is_called(mock_random: Mock, seq: list):
    pick_random_element(seq)

    mock_random.seed.assert_called_once(), "random.seed called"
    mock_random.randrange.assert_called_with(len(seq)), "random.randrange called"
