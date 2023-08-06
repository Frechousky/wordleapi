import dataclasses
import enum

import flask

from wordleapi.core import (
    GUESS_REGEX,
    GuessInvalidFormatError,
    GuessIsEmptyError,
    GuessNotInWhitelistError,
    InvalidGuessLengthError,
    compute_guess_result,
    validate_guess,
)

WHITELIST = ["wordle", "arbres"]
WORD = "wordle"


class ErrorCode(enum.IntEnum):
    HPG_INVALID_GUESS_LENGTH = 100
    HPG_EMPTY_GUESS = 101
    HPG_INVALID_FORMAT = 102
    HPG_GUESS_NOT_IN_WHITELIST = 103


@dataclasses.dataclass
class ApiError:
    code: ErrorCode
    error: str


def create_app() -> flask.Flask:
    app = flask.Flask(__name__)

    @app.route("/word/guess", methods=["POST"])
    def handle_player_guess():
        guess = flask.request.form.get("guess", None)
        try:
            validate_guess(guess, WORD, WHITELIST)
        except InvalidGuessLengthError as e:
            return (
                ApiError(
                    ErrorCode.HPG_INVALID_GUESS_LENGTH,
                    f"'{guess}' is not {e.expected_length()} letters long",
                ).__dict__,
                422,
            )
        except GuessIsEmptyError:
            return (
                ApiError(
                    ErrorCode.HPG_EMPTY_GUESS,
                    "no guess value submitted",
                ).__dict__,
                422,
            )
        except GuessInvalidFormatError:
            return (
                ApiError(
                    ErrorCode.HPG_INVALID_FORMAT,
                    f"'{guess}' format is invalid (should match regex {GUESS_REGEX})",
                ).__dict__,
                422,
            )
        except GuessNotInWhitelistError:
            return (
                ApiError(
                    ErrorCode.HPG_GUESS_NOT_IN_WHITELIST,
                    f"'{guess}' is not in whitelist",
                ).__dict__,
                422,
            )
        return compute_guess_result(guess, WORD).__dict__, 200

    return app
