import pytest

from wordleapi.core import (
    compute_attempt_result,
    LetterPositionStatus as LPS,
)


@pytest.mark.parametrize("attempt,answer", [("abcdef", "abcdef"), ("zyxwvu", "zyxwvu")])
def test_compute_attempt_result__valid_attempt(attempt: str, answer: str):
    assert compute_attempt_result(attempt, answer) == []


@pytest.mark.parametrize(
    "attempt,answer,expected_result",
    [
        # only not present letters
        ("abcdef", "zyxwvu", [LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        # 1-5 letter(s) at good position
        ("abcdef", "azyxwv", [LPS.GP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "azcxwv", [LPS.GP, LPS.NP, LPS.GP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "azcxwf", [LPS.GP, LPS.NP, LPS.GP, LPS.NP, LPS.NP, LPS.GP]),
        ("abcdef", "abcxwf", [LPS.GP, LPS.GP, LPS.GP, LPS.NP, LPS.NP, LPS.GP]),
        ("abcdef", "abcxef", [LPS.GP, LPS.GP, LPS.GP, LPS.NP, LPS.GP, LPS.GP]),
        # 1-6 letters at bad position
        ("abcdef", "zayxwv", [LPS.BP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "zaxwvc", [LPS.BP, LPS.NP, LPS.BP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "faxwvc", [LPS.BP, LPS.NP, LPS.BP, LPS.NP, LPS.NP, LPS.BP]),
        ("abcdef", "fabwvc", [LPS.BP, LPS.BP, LPS.BP, LPS.NP, LPS.NP, LPS.BP]),
        ("abcdef", "fabwdc", [LPS.BP, LPS.BP, LPS.BP, LPS.BP, LPS.NP, LPS.BP]),
        ("abcdef", "fabedc", [LPS.BP, LPS.BP, LPS.BP, LPS.BP, LPS.BP, LPS.BP]),
        # good & bad position mix
        ("abcdef", "afzyxw", [LPS.GP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.BP]),
        ("abcdef", "abdcef", [LPS.GP, LPS.GP, LPS.BP, LPS.BP, LPS.GP, LPS.GP]),
        # letter present multiple times
        ("aacdef", "aazyxw", [LPS.GP, LPS.GP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("aacdef", "azyxwa", [LPS.GP, LPS.BP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("aacdef", "azyxwv", [LPS.GP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "aayxwv", [LPS.GP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("adaeaf", "azyxwv", [LPS.GP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "ayxawa", [LPS.GP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        # anagrams
        ("tartes", "rattes", [LPS.BP, LPS.GP, LPS.BP, LPS.GP, LPS.GP, LPS.GP]),
        ("tartes", "restat", [LPS.BP, LPS.BP, LPS.BP, LPS.GP, LPS.BP, LPS.BP]),
        ("tartes", "sterat", [LPS.BP, LPS.BP, LPS.BP, LPS.BP, LPS.BP, LPS.BP]),
        ("tartes", "strate", [LPS.BP, LPS.BP, LPS.GP, LPS.BP, LPS.BP, LPS.BP]),
        ("tartes", "tarets", [LPS.GP, LPS.GP, LPS.GP, LPS.BP, LPS.BP, LPS.GP]),
        ("tartes", "tersat", [LPS.GP, LPS.BP, LPS.GP, LPS.BP, LPS.BP, LPS.BP]),
        ("tartes", "tetras", [LPS.GP, LPS.BP, LPS.BP, LPS.BP, LPS.BP, LPS.GP]),
        # it's a me
        ("itsame", "maario", [LPS.BP, LPS.NP, LPS.NP, LPS.BP, LPS.BP, LPS.NP]),
    ],
)
def test_compute_attempt_result__invalid_attempt(
    attempt: str, answer: str, expected_result: tuple[LPS]
):
    assert (
        compute_attempt_result(attempt, answer) == expected_result
    ), f'attempt: "{attempt}", answer: "{answer}"'
