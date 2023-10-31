from unittest.mock import patch, Mock

import pytest

from wordleapi.core import get_today_word
from wordleapi.db.model import PlayedWord
from wordleapi.utils import now_yyyymmdd


@pytest.mark.parametrize(
    "word,whitelist,played_words",
    (
        ("arbres", ("arbres",), []),
        (
            "joutera",
            ("joutera", "pipames", "temenos"),
            [PlayedWord(word="pipames", word_length=7)],
        ),
        (
            "retameur",
            ("abatardi", "cyclable", "gaillard", "retameur", "zwieback"),
            [
                PlayedWord(word="abatardi", word_length=8),
                PlayedWord(word="cyclable", word_length=8),
                PlayedWord(word="gaillard", word_length=8),
            ],
        ),
    ),
)
@patch("wordleapi.core.commit")
@patch("wordleapi.core.add_played_word")
@patch("wordleapi.core.pick_random_element")
@patch("wordleapi.core.delete_played_word_by_word_length")
@patch("wordleapi.core.get_all_played_word_by_word_length")
@patch("wordleapi.core.get_first_played_word_by_word_length_and_date")
def test_get_today_word__if_all_whitelisted_words_were_not_played__does_not_delete_played_words(
    mock_get_first_word: Mock,
    mock_get_all_word: Mock,
    mock_delete_word: Mock,
    mock_pick_random: Mock,
    mock_add_word: Mock,
    mock_commit: Mock,
    word: str,
    whitelist: tuple[str],
    played_words: list[PlayedWord],
):
    word_length = len(word)

    mock_get_first_word.return_value = None
    mock_get_all_word.return_value = played_words
    mock_pick_random.return_value = word

    assert get_today_word(whitelist) == word

    mock_get_first_word.assert_called_with(
        word_length, now_yyyymmdd()
    ), "should retrieve today word"
    mock_get_all_word.assert_called_with(
        word_length
    ), "should retrieve played word from database"
    mock_delete_word.assert_not_called(), "should not delete played words from database"
    mock_add_word.assert_called_once_with(
        word, len(word)
    ), "should add word to database"
    mock_commit.assert_called_once(), "should commit"


@pytest.mark.parametrize("word", ("arbres", "joutera", "retameur"))
@patch("wordleapi.core.commit")
@patch("wordleapi.core.add_played_word")
@patch("wordleapi.core.pick_random_element")
@patch("wordleapi.core.delete_played_word_by_word_length")
@patch("wordleapi.core.get_all_played_word_by_word_length")
@patch("wordleapi.core.get_first_played_word_by_word_length_and_date")
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

    mock_get_first_word.return_value = PlayedWord(word=word, word_length=word_length)

    assert get_today_word(tuple([word])) == word

    mock_get_first_word.assert_called_with(
        word_length, now_yyyymmdd()
    ), "should retrieve today word"
    mock_get_all_word.assert_not_called(), "should not retrieve played word from database"
    mock_delete_word.assert_not_called(), "should not delete played words from database"
    mock_pick_random.assert_not_called(), "should not pick random word"
    mock_add_word.assert_not_called(), "should not add word to database"
    mock_commit.assert_not_called(), "should not commit"


@pytest.mark.parametrize(
    "word,whitelist,played_words",
    (
        (
            "arbres",
            ("arbres",),
            [
                PlayedWord(word="arbres", word_length=6),
                PlayedWord(word="cassis", word_length=6),
            ],
        ),
        (
            "joutera",
            ("joutera", "pipames", "temenos"),
            [
                PlayedWord(word="joutera", word_length=7),
                PlayedWord(word="pipames", word_length=7),
                PlayedWord(word="temenos", word_length=7),
                PlayedWord(word="telefax", word_length=7),
                PlayedWord(word="jingxis", word_length=7),
            ],
        ),
        (
            "retameur",
            ("abatardi", "cyclable", "gaillard", "retameur", "zwieback"),
            [
                PlayedWord(word="abatardi", word_length=8),
                PlayedWord(word="cyclable", word_length=8),
                PlayedWord(word="gaillard", word_length=8),
                PlayedWord(word="retameur", word_length=8),
                PlayedWord(word="zwieback", word_length=8),
            ],
        ),
    ),
)
@patch("wordleapi.core.commit")
@patch("wordleapi.core.add_played_word")
@patch("wordleapi.core.pick_random_element")
@patch("wordleapi.core.delete_played_word_by_word_length")
@patch("wordleapi.core.get_all_played_word_by_word_length")
@patch("wordleapi.core.get_first_played_word_by_word_length_and_date")
def test_get_today_word__if_all_whitelisted_words_were_played__deletes_played_words(
    mock_get_first_word: Mock,
    mock_get_all_word: Mock,
    mock_delete_word: Mock,
    mock_pick_random: Mock,
    mock_add_word: Mock,
    mock_commit: Mock,
    word: str,
    whitelist: tuple[str],
    played_words: list[PlayedWord],
):
    word_length = len(word)

    mock_get_first_word.return_value = None
    mock_get_all_word.return_value = played_words
    mock_pick_random.return_value = word

    assert get_today_word(whitelist) == word

    mock_get_first_word.assert_called_with(
        word_length, now_yyyymmdd()
    ), "should retrieve today word"
    mock_get_all_word.assert_called_with(
        word_length
    ), "should retrieve played word from database"
    mock_delete_word.assert_called_with(
        word_length
    ), "should delete played words from database"
    mock_add_word.assert_called_once_with(
        word, len(word)
    ), "should add word to database"
    mock_commit.assert_called_once(), "should commit"
