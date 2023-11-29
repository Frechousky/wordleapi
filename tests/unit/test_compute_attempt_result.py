import pytest

from wordleapi.core import (
    compute_attempt_result,
    LetterPositionStatus as LPS,
)


@pytest.mark.parametrize("attempt,answer", [("abcdef", "abcdef"), ("zyxwvu", "zyxwvu")])
def test_compute_attempt_result__valid_attempt(attempt: str, answer: str):
    assert compute_attempt_result(attempt, answer) == [LPS.WP] * len(attempt)


@pytest.mark.parametrize(
    "attempt,answer,expected_result",
    [
        # only not present letters
        ("abcdef", "zyxwvu", [LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        # 1-5 letter(s) at good position
        ("abcdef", "azyxwv", [LPS.WP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "azcxwv", [LPS.WP, LPS.NP, LPS.WP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "azcxwf", [LPS.WP, LPS.NP, LPS.WP, LPS.NP, LPS.NP, LPS.WP]),
        ("abcdef", "abcxwf", [LPS.WP, LPS.WP, LPS.WP, LPS.NP, LPS.NP, LPS.WP]),
        ("abcdef", "abcxef", [LPS.WP, LPS.WP, LPS.WP, LPS.NP, LPS.WP, LPS.WP]),
        # 1-6 letters at bad position
        ("abcdef", "zayxwv", [LPS.MP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "zaxwvc", [LPS.MP, LPS.NP, LPS.MP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "faxwvc", [LPS.MP, LPS.NP, LPS.MP, LPS.NP, LPS.NP, LPS.MP]),
        ("abcdef", "fabwvc", [LPS.MP, LPS.MP, LPS.MP, LPS.NP, LPS.NP, LPS.MP]),
        ("abcdef", "fabwdc", [LPS.MP, LPS.MP, LPS.MP, LPS.MP, LPS.NP, LPS.MP]),
        ("abcdef", "fabedc", [LPS.MP, LPS.MP, LPS.MP, LPS.MP, LPS.MP, LPS.MP]),
        # good & bad position mix
        ("abcdef", "afzyxw", [LPS.WP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.MP]),
        ("abcdef", "abdcef", [LPS.WP, LPS.WP, LPS.MP, LPS.MP, LPS.WP, LPS.WP]),
        # letter present multiple times
        ("aacdef", "aazyxw", [LPS.WP, LPS.WP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("aacdef", "azyxwa", [LPS.WP, LPS.MP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("aacdef", "azyxwv", [LPS.WP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "aayxwv", [LPS.WP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("adaeaf", "azyxwv", [LPS.WP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        ("abcdef", "ayxawa", [LPS.WP, LPS.NP, LPS.NP, LPS.NP, LPS.NP, LPS.NP]),
        # anagrams
        ("tartes", "rattes", [LPS.MP, LPS.WP, LPS.MP, LPS.WP, LPS.WP, LPS.WP]),
        ("tartes", "restat", [LPS.MP, LPS.MP, LPS.MP, LPS.WP, LPS.MP, LPS.MP]),
        ("tartes", "sterat", [LPS.MP, LPS.MP, LPS.MP, LPS.MP, LPS.MP, LPS.MP]),
        ("tartes", "strate", [LPS.MP, LPS.MP, LPS.WP, LPS.MP, LPS.MP, LPS.MP]),
        ("tartes", "tarets", [LPS.WP, LPS.WP, LPS.WP, LPS.MP, LPS.MP, LPS.WP]),
        ("tartes", "tersat", [LPS.WP, LPS.MP, LPS.WP, LPS.MP, LPS.MP, LPS.MP]),
        ("tartes", "tetras", [LPS.WP, LPS.MP, LPS.MP, LPS.MP, LPS.MP, LPS.WP]),
        # it's a me
        ("itsame", "maario", [LPS.MP, LPS.NP, LPS.NP, LPS.MP, LPS.MP, LPS.NP]),
    ],
)
def test_compute_attempt_result__invalid_attempt(
    attempt: str, answer: str, expected_result: tuple[LPS]
):
    assert (
        compute_attempt_result(attempt, answer) == expected_result
    ), f'attempt: "{attempt}", answer: "{answer}"'
