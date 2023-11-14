import pytest

from wordleapi.core import (
    AttemptInvalidFormatError,
    AttemptIsEmptyError,
    AttemptNotInWhitelistError,
    InvalidAttemptLengthError,
    validate_attempt,
)

WHITELIST = ("abcdef", "zyxwvu")


@pytest.mark.parametrize(
    "attempt",
    [
        "",
        None,
    ],
)
def test_validate_attempt__attempt_is_none__raises_exception(attempt: str):
    with pytest.raises(AttemptIsEmptyError):
        validate_attempt(attempt, WHITELIST)


@pytest.mark.parametrize(
    "attempt",
    ["abcde", "abcdefgh"],
)
def test_validate_attempt__wrong_sized_attempt__raises_exception(attempt: str):
    with pytest.raises(InvalidAttemptLengthError):
        validate_attempt(attempt, WHITELIST)


@pytest.mark.parametrize(
    "attempt",
    [
        "123aze",
        "@çazer",
    ],
)
def test_validate_attempt__attempt_invalid_format__raises_exception(attempt: str):
    with pytest.raises(AttemptInvalidFormatError):
        validate_attempt(attempt, WHITELIST)


@pytest.mark.parametrize(
    "attempt,whitelist",
    [
        ("ghijkl", WHITELIST),
        ("mnopqr", WHITELIST),
    ],
)
def test_validate_attempt__attempt_not_in_whitelist__raises_exception(
    attempt: str, whitelist: list[str]
):
    assert attempt not in whitelist

    with pytest.raises(AttemptNotInWhitelistError):
        validate_attempt(attempt, whitelist)


def test_validate_attempt__valid_attempt__returns_true():
    for attempt in WHITELIST:
        assert validate_attempt(attempt, WHITELIST)
