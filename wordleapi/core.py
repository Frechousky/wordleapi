import enum

import loguru

from wordleapi.db.model import (
    add_played_word,
    commit,
    delete_played_word_by_word_length,
    get_all_played_word_by_word_length,
    get_first_played_word_by_word_length_and_date,
)
from wordleapi.utils import now_yyyymmdd, pick_random_element


# Available/playable word length
AVAILABLE_WORD_LENGTHS = [6, 7, 8]


class LetterPositionStatus(enum.IntEnum):
    """
    0 (well-placed),
    1 (misplaced),
    2 (not present)
    """

    WP = 0  # well-placed
    MP = 1  # misplaced
    NP = 2  # not present


ATTEMPT_REGEX = "^[a-zA-Z]+$"


def compute_attempt_result(attempt: str, word: str) -> list[LetterPositionStatus]:
    """
    Check if player attempt is correct.

    Args:
        attempt: player attempt
        word: word to find

    Returns:
        List of position status (either not present, bad position or good position) for each letter in attempt
    """
    assert attempt
    assert word

    # attempt is correct
    if attempt == word:
        result = [LetterPositionStatus.WP] * len(word)
        loguru.logger.debug(
            "(attempt: '{}', word: '{}') => {} (correct attempt)", attempt, word, result
        )
        return result

    # look for good positioned letters
    available_word_letters = [letter for letter in word]
    result = len(attempt) * [LetterPositionStatus.NP]
    for idx, v in enumerate(attempt):
        if word[idx] == v:
            result[idx] = LetterPositionStatus.WP
            available_word_letters[idx] = None

    # look for bad positioned letters
    for idx, v in enumerate(attempt):
        if result[idx] == LetterPositionStatus.WP:
            continue
        try:
            awl_idx = available_word_letters.index(v)
            result[idx] = LetterPositionStatus.MP
            available_word_letters[awl_idx] = None
        except ValueError:
            pass

    loguru.logger.debug(
        "(attempt: '{}', word: '{}') => {} (incorrect attempt)",
        attempt,
        word,
        [lps.value for lps in result],
    )
    return result


def load_whitelist_file(filename: str) -> tuple[str]:
    """
    Load whitelist file and extract list of words from it.

    Args:
        filename: file to read

    Returns:
        Word list

    Raises:
        OSError: if file opening fails
    """
    loguru.logger.info("Load whitelist file '{}'", filename)
    with open(filename) as f:
        whitelist = tuple([word for word in f.read().split("\n") if word != ""])
        loguru.logger.info("Found {} words in '{}'", len(whitelist), filename)
        return whitelist


def get_today_word(whitelist: tuple[str]) -> str:
    """
    Get today word to guess by retrieving it from database or picking a random non-played word.

    Played word are stored in database.
    If today word is in database returns it, otherwise pick a random word from whitelist which is not in played word
    database and returns it.
    If all whitelist words have already been played, clean played word from database.

    Args:
        whitelist: list of available words

    Returns:
        Today word to guess
    """
    assert whitelist

    word_length = len(whitelist[0])

    # check if today's word is already generated
    today_word = get_first_played_word_by_word_length_and_date(
        word_length, now_yyyymmdd()
    )
    if today_word:
        loguru.logger.debug("Today {} letters word already generated", word_length)
        return today_word.word

    # retrieve already played words
    loguru.logger.info("Generate today {} letters word", word_length)
    already_played_words = get_all_played_word_by_word_length(word_length)

    available_words = tuple(
        set(whitelist) - set(wh.word for wh in already_played_words)
    )

    if not available_words:
        # all whitelisted words were played
        # clean played_word table
        loguru.logger.info(
            "All {} letters word were played, clean played_word table", word_length
        )
        delete_played_word_by_word_length(word_length)
        available_words = whitelist
    loguru.logger.info(
        "{} available {} letters word", len(available_words), word_length
    )

    # pick random word
    word = pick_random_element(available_words)
    loguru.logger.info("Today {} letters word is '{}'", word_length, word)

    # save word to database
    add_played_word(word, word_length)
    commit()

    return word
