from unittest.mock import patch, Mock

import pytest

from wordleapi import get_today_word
from wordleapi.db.model import WordHistory
from wordleapi.utils import now_yyyymmdd


@pytest.mark.parametrize(
    "word,whitelist,word_history",
    (
        ("arbres", ("arbres",), []),
        (
            "joutera",
            ("joutera", "pipames", "temenos"),
            [WordHistory(word="pipames", word_length=7)],
        ),
        (
            "retameur",
            ("abatardi", "cyclable", "gaillard", "retameur", "zwieback"),
            [
                WordHistory(word="abatardi", word_length=8),
                WordHistory(word="cyclable", word_length=8),
                WordHistory(word="gaillard", word_length=8),
            ],
        ),
    ),
)
@patch("wordleapi.core.commit")
@patch("wordleapi.core.add_word_history")
@patch("wordleapi.core.pick_random_element")
@patch("wordleapi.core.delete_word_history_by_word_length")
@patch("wordleapi.core.get_all_word_history_by_word_length")
@patch("wordleapi.core.get_first_word_history_by_word_length_and_date")
def test_get_today_word__if_all_whitelisted_word_are_not_in_history__does_not_delete_history(
    mock_get_first_word: Mock,
    mock_get_all_word: Mock,
    mock_delete_word: Mock,
    mock_pick_random: Mock,
    mock_add_word: Mock,
    mock_commit: Mock,
    word: str,
    whitelist: tuple[str],
    word_history: list[WordHistory],
):
    word_length = len(word)

    mock_get_first_word.return_value = None
    mock_get_all_word.return_value = word_history
    mock_pick_random.return_value = word

    assert get_today_word(whitelist) == word

    mock_get_first_word.assert_called_with(
        word_length, now_yyyymmdd()
    ), "should retrieve today word"
    mock_get_all_word.assert_called_with(
        word_length
    ), "should retrieve word history from database"
    mock_delete_word.assert_not_called(), "should not delete word history from database"
    mock_add_word.assert_called_once_with(
        word, len(word)
    ), "should add word to database"
    mock_commit.assert_called_once(), "should commit"


@pytest.mark.parametrize("word", ("arbres", "joutera", "retameur"))
@patch("wordleapi.core.commit")
@patch("wordleapi.core.add_word_history")
@patch("wordleapi.core.pick_random_element")
@patch("wordleapi.core.delete_word_history_by_word_length")
@patch("wordleapi.core.get_all_word_history_by_word_length")
@patch("wordleapi.core.get_first_word_history_by_word_length_and_date")
def test_get_today_word__if_today_word_was_generated__returns_it(
    mock_get_first_word: Mock,
    mock_get_all_word: Mock,
    mock_delete_word: Mock,
    mock_pick_random: Mock,
    mock_add_word: Mock,
    mock_commit: Mock,
    word: str,
):
    word_length = len(word)

    mock_get_first_word.return_value = WordHistory(word=word, word_length=word_length)

    assert get_today_word(tuple([word])) == word

    mock_get_first_word.assert_called_with(
        word_length, now_yyyymmdd()
    ), "should retrieve today word"
    mock_get_all_word.assert_not_called(), "should not retrieve word history from database"
    mock_delete_word.assert_not_called(), "should not delete word history from database"
    mock_pick_random.assert_not_called(), "should not pick random word"
    mock_add_word.assert_not_called(), "should not add word to database"
    mock_commit.assert_not_called(), "should not commit"


@pytest.mark.parametrize(
    "word,whitelist",
    (
        ("arbres", ("arbres",)),
        ("joutera", ("joutera", "pipames", "temenos")),
        ("retameur", ("abatardi", "cyclable", "gaillard", "retameur", "zwieback")),
    ),
)
@patch("wordleapi.core.commit")
@patch("wordleapi.core.add_word_history")
@patch("wordleapi.core.pick_random_element")
@patch("wordleapi.core.delete_word_history_by_word_length")
@patch("wordleapi.core.get_all_word_history_by_word_length")
@patch("wordleapi.core.get_first_word_history_by_word_length_and_date")
def test_get_today_word__if_all_whitelisted_word_are_in_history__deletes_history(
    mock_get_first_word: Mock,
    mock_get_all_word: Mock,
    mock_delete_word: Mock,
    mock_pick_random: Mock,
    mock_add_word: Mock,
    mock_commit: Mock,
    word: str,
    whitelist: tuple[str],
):
    word_length = len(word)

    mock_get_first_word.return_value = None
    mock_get_all_word.return_value = [
        WordHistory(word=word, word_length=word_length) for word in whitelist
    ]  # all whitelisted word are in history
    mock_pick_random.return_value = word

    assert get_today_word(whitelist) == word

    mock_get_first_word.assert_called_with(
        word_length, now_yyyymmdd()
    ), "should retrieve today word"
    mock_get_all_word.assert_called_with(
        word_length
    ), "should retrieve word history from database"
    mock_delete_word.assert_called_with(
        word_length
    ), "should delete word history from database"
    mock_add_word.assert_called_once_with(
        word, len(word)
    ), "should add word to database"
    mock_commit.assert_called_once(), "should commit"
