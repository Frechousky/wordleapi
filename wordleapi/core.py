import dataclasses
import enum
import re


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


    Args:
        guess (str): _description_
        word (str): _description_

    Returns:
        GuessResult: _description_
    """
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
        try:
            if result[idx] == LetterPositionStatus.GP:
                continue
            awl_idx = available_word_letters.index(v)
            result[idx] = LetterPositionStatus.BP
            available_word_letters[awl_idx] = None
        except ValueError:
            pass

    return GuessResult(False, tuple(result))
