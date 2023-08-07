import dataclasses
import enum
import random
import re

import loguru

from wordleapi.db.model import (
    add_word_history,
    commit,
    delete_word_history_by_word_length,
    get_all_word_history_by_word_length,
    get_first_word_history_by_word_length_and_date,
)
from wordleapi.utils import now_yyyymmdd


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


@dataclasses.dataclass
class GuessResult:
    """
    Dataclass to handle player guess result.

    Attributes:
        success: true if player guessed the word, false otherwise
        result: contains letter position status (good/bad position or not present)
                for each letter from player guess
    """

    success: bool
    result: tuple[LetterPositionStatus]


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
        True if the guess is valid, otherwise it raises an error

    Raises:
        GuessIsEmptyError: if guess is None or ""
        InvalidGuessLengthError: if guess length is not equal to word length
        GuessInvalidFormatError: if guess is not only characters (lower/upper case)
        GuessNotInWhitelistError: if guess is not a whitelisted word
    """
    assert whitelist

    if not guess:
        raise GuessIsEmptyError()
    if len(guess) != len(whitelist[0]):
        raise InvalidGuessLengthError(len(whitelist[0]))
    if GUESS_PATTERN.fullmatch(guess) is None:
        raise GuessInvalidFormatError()
    if guess not in whitelist:
        raise GuessNotInWhitelistError()
    return True


def compute_guess_result(guess: str, word: str) -> GuessResult:
    """
    Check if player guess is correct.

    Compare player guess with word to find and returns a GuessResult.

    Args:
        guess: player guess
        word: word to find

    Returns:
        GuessResult with success to True if guess is correct,
        GuessResult with success to False and letter status
        (either not present, bad position or good position) for each
        guessed letter
    """
    assert guess
    assert word

    # guess is correct
    if guess == word:
        return GuessResult(True, None)

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

    return GuessResult(False, tuple(result))


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
    loguru.logger.debug("Load wordlefile '{}'", filename)
    with open(filename) as f:
        whitelist = tuple([word for word in f.read().split("\n") if word != ""])
        loguru.logger.debug(f"Found {len(whitelist)} words")
        return whitelist


def get_current_word(whitelist: tuple[str]) -> str:
    assert whitelist

    word_length = len(whitelist[0])

    # check if today's word is already generated
    today_word = get_first_word_history_by_word_length_and_date(
        word_length, now_yyyymmdd()
    )
    if today_word:
        return today_word.word

    # retrieve used words
    words_history = get_all_word_history_by_word_length(word_length)

    used_words = set(wh.word for wh in words_history)
    available_words = list(set(whitelist) - used_words)
    if not len(available_words):
        # all whitelisted words were used
        # delete all WordHistory records where word_length=word_length
        delete_word_history_by_word_length(word_length)
        available_words = whitelist

    # pick random available word
    random.seed()
    word = available_words[random.randint(0, len(available_words) - 1)]

    add_word_history(word, word_length)
    commit()
    return word
