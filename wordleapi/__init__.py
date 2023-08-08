import enum
import os

import dotenv
import flask
import loguru

from wordleapi.core import (
    GUESS_REGEX,
    GuessInvalidFormatError,
    GuessIsEmptyError,
    GuessNotInWhitelistError,
    InvalidGuessLengthError,
    compute_guess_result,
    get_today_word,
    load_wordlefile,
    validate_guess,
)
from wordleapi.db.model import db
from wordleapi.env import DotEnvKey


class ErrorCode(enum.Enum):
    HPG_INVALID_GUESS_LENGTH = 100
    HPG_EMPTY_GUESS = 101
    HPG_INVALID_FORMAT = 102
    HPG_GUESS_NOT_IN_WHITELIST = 103


def build_error_response(code: ErrorCode, error_msg: str) -> dict:
    return {"code": code.value, "error_msg": error_msg}


def handle_player_guess(whitelist: tuple[str]):
    guess = flask.request.form.get("guess", None)
    try:
        validate_guess(guess, whitelist)
    except InvalidGuessLengthError as e:
        return (
            build_error_response(
                ErrorCode.HPG_INVALID_GUESS_LENGTH,
                f"'{guess}' is not {e.expected_length()} letters long",
            ),
            422,
        )
    except GuessIsEmptyError:
        return (
            build_error_response(
                ErrorCode.HPG_EMPTY_GUESS,
                "no guess value submitted",
            ),
            422,
        )
    except GuessInvalidFormatError:
        return (
            build_error_response(
                ErrorCode.HPG_INVALID_FORMAT,
                f"'{guess}' format is invalid (should match regex {GUESS_REGEX})",
            ),
            422,
        )
    except GuessNotInWhitelistError:
        return (
            build_error_response(
                ErrorCode.HPG_GUESS_NOT_IN_WHITELIST,
                f"'{guess}' is not in whitelist",
            ),
            422,
        )
    word = get_today_word(whitelist)
    loguru.logger.info(f"word: {word}, guess: {guess}")

    guess_result = compute_guess_result(guess, word)

    if not guess_result:
        return {"success": True}

    return {"success": False, "result": guess_result}


def create_app() -> flask.Flask:
    dotenv.load_dotenv(verbose=True)

    app = flask.Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        DotEnvKey.SQLALCHEMY_DATABASE_URI.value
    )

    db.init_app(app)

    with app.app_context():
        db.create_all()

    whitelist_6_letters = load_wordlefile(
        os.getenv(DotEnvKey.WORDLEFILE_6_LETTERS.value)
    )
    whitelist_7_letters = load_wordlefile(
        os.getenv(DotEnvKey.WORDLEFILE_7_LETTERS.value)
    )
    whitelist_8_letters = load_wordlefile(
        os.getenv(DotEnvKey.WORDLEFILE_8_LETTERS.value)
    )

    @app.route("/word/6/guess", methods=["POST"])
    def handle_player_guess_six_letters():
        return handle_player_guess(whitelist_6_letters)

    @app.route("/word/7/guess", methods=["POST"])
    def handle_player_guess_seven_letters():
        return handle_player_guess(whitelist_7_letters)

    @app.route("/word/8/guess", methods=["POST"])
    def handle_player_guess_eight_letters():
        return handle_player_guess(whitelist_8_letters)

    return app
