import pytest

from wordleapi.core import (
    GuessInvalidFormatError,
    GuessIsEmptyError,
    GuessNotInWhitelistError,
    InvalidGuessLengthError,
    validate_guess,
)

WHITELIST = ["abcdef", "zyxwv"]
WORD = "abcdef"


@pytest.mark.parametrize(
    "guess",
    [
        "",
        None,
    ],
)
def test_validate_guess__guess_is_none__raises_exception(guess: str):
    with pytest.raises(GuessIsEmptyError):
        validate_guess(guess, WORD, WHITELIST)


@pytest.mark.parametrize(
    "guess,word",
    [
        ("abcde", "abcdef"),
        ("abcdefgh", "abcdef"),
    ],
)
def test_validate_guess__wrong_sized_guess__raises_exception(guess: str, word: str):
    with pytest.raises(InvalidGuessLengthError):
        validate_guess(guess, word, WHITELIST)


@pytest.mark.parametrize(
    "guess",
    [
        "123aze",
        "@çazer",
    ],
)
def test_validate_guess__guess_invalid_format__raises_exception(guess: str):
    with pytest.raises(GuessInvalidFormatError):
        validate_guess(guess, WORD, WHITELIST)


@pytest.mark.parametrize(
    "guess,whitelist",
    [
        ("ghijkl", WHITELIST),
        ("mnopqr", WHITELIST),
    ],
)
def test_validate_guess__guess_not_in_whitelist__raises_exception(
    guess: str, whitelist: list[str]
):
    assert guess not in whitelist

    with pytest.raises(GuessNotInWhitelistError):
        validate_guess(guess, WORD, whitelist)


def test_validate_guess__valid_guess__returns_true():
    for guess in WHITELIST:
        assert validate_guess(guess, guess, WHITELIST)
