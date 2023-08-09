import enum
import re

import loguru

from wordleapi.db.model import (
    add_played_word,
    commit,
    delete_played_word_by_word_length,
    get_all_played_word_by_word_length,
    get_first_played_word_by_word_length_and_date,
)
from wordleapi.utils import now_yyyymmdd, pick_random_element


class GuessIsEmptyError(Exception):
    pass


class InvalidGuessLengthError(Exception):
    def __init__(self, expected_length: int, *args: object) -> None:
        super().__init__(*args)
        self.__expected_length = expected_length

    def expected_length(self) -> int:
        return self.__expected_length


class GuessNotInWhitelistError(Exception):
    pass


class GuessInvalidFormatError(Exception):
    pass


class LetterPositionStatus(enum.IntEnum):
    GP = 0  # good position
    BP = 1  # bad position
    NP = 2  # not present


GUESS_REGEX = "[a-zA-Z]+"
GUESS_PATTERN = re.compile(GUESS_REGEX)


def validate_guess(guess: str, whitelist: tuple[str]) -> bool:
    """
    Validate user guess input.
    Raises exception if guess is invalid, returns True otherwise.

    Args:
        guess: Store the user's guess
        whitelist: Check if the guess is in the whitelist

    Returns:
        True if the guess is valid

    Raises:
        GuessIsEmptyError: if guess is None or ""
        InvalidGuessLengthError: if guess length is not equal to word length
        GuessInvalidFormatError: if guess is not only characters (lower/upper case)
        GuessNotInWhitelistError: if guess is not a whitelisted word
    """
    assert whitelist

    loguru.logger.debug("(guess: '{}')", guess)

    if not guess:
        loguru.logger.debug("(guess: '{}') => GuessIsEmptyError", guess)
        raise GuessIsEmptyError()
    if len(guess) != len(whitelist[0]):
        loguru.logger.debug("(guess: '{}') => InvalidGuessLengthError", guess)
        raise InvalidGuessLengthError(len(whitelist[0]))
    if GUESS_PATTERN.fullmatch(guess) is None:
        loguru.logger.debug("(guess: '{}') => GuessInvalidFormatError", guess)
        raise GuessInvalidFormatError()
    if guess not in whitelist:
        loguru.logger.debug("(guess: '{}') => GuessNotInWhitelistError", guess)
        raise GuessNotInWhitelistError()

    loguru.logger.debug("(guess: '{}') => True", guess)
    return True


def compute_guess_result(guess: str, word: str) -> list[LetterPositionStatus]:
    """
    Check if player guess is correct.

    Args:
        guess: player guess
        word: word to find

    Returns:
        [] if guess is correct
        List of position status (either not present, bad position or good position) for each letter in guess
    """
    assert guess
    assert word

    # guess is correct
    if guess == word:
        loguru.logger.debug(
            "(guess: '{}', word: '{}') => [] (correct guess)", guess, word
        )
        return []

    # look for good positioned letters
    available_word_letters = [letter for letter in word]
    result = len(guess) * [LetterPositionStatus.NP]
    for idx, v in enumerate(guess):
        if word[idx] == v:
            result[idx] = LetterPositionStatus.GP
            available_word_letters[idx] = None

    # look for bad positioned letters
    for idx, v in enumerate(guess):
        if result[idx] == LetterPositionStatus.GP:
            continue
        try:
            awl_idx = available_word_letters.index(v)
            result[idx] = LetterPositionStatus.BP
            available_word_letters[awl_idx] = None
        except ValueError:
            pass

    loguru.logger.debug(
        "(guess: '{}', word: '{}') => {} (incorrect guess)",
        guess,
        word,
        [lps.value for lps in result],
    )
    return result


def load_wordlefile(filename: str) -> tuple[str]:
    """
    Load wordlefile and extract list of words from it.

    Args:
        filename: file to read

    Returns:
        Word list

    Raises:
        OSError: if file opening fails
    """
    loguru.logger.info("Load wordlefile '{}'", filename)
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
        Today word
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
