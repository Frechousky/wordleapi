import enum
import os

import dotenv
import flask
import flask_cors
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
from wordleapi.env import DotEnvKey, check_dot_env
from wordleapi.utils import strip_lower


class ErrorCode(enum.Enum):
    INVALID_GUESS_LENGTH = 100
    EMPTY_GUESS = 101
    INVALID_FORMAT = 102
    GUESS_NOT_IN_WHITELIST = 103


def build_error_response(code: ErrorCode, error_msg: str) -> dict:
    return {"code": code.value, "error_msg": error_msg}


def handle_player_guess(whitelist: tuple[str]):
    guess = strip_lower(flask.request.form.get("guess", None))
    loguru.logger.debug("(guess: '{}')", guess)
    try:
        validate_guess(guess, whitelist)
    except InvalidGuessLengthError as e:
        return (
            build_error_response(
                ErrorCode.INVALID_GUESS_LENGTH,
                f"'{guess}' is not {e.expected_length()} letters long",
            ),
            422,
        )
    except GuessIsEmptyError:
        return (
            build_error_response(
                ErrorCode.EMPTY_GUESS,
                "no guess value submitted",
            ),
            422,
        )
    except GuessInvalidFormatError:
        return (
            build_error_response(
                ErrorCode.INVALID_FORMAT,
                f"'{guess}' format is invalid (should match regex {GUESS_REGEX})",
            ),
            422,
        )
    except GuessNotInWhitelistError:
        return (
            build_error_response(
                ErrorCode.GUESS_NOT_IN_WHITELIST,
                f"'{guess}' is not in whitelist",
            ),
            422,
        )
    word = get_today_word(whitelist)
    guess_result = compute_guess_result(guess, word)

    if not guess_result:
        return {"success": True}

    return {"success": False, "result": guess_result}


def create_app() -> flask.Flask:
    loguru.logger.info("Init app")

    if dotenv.load_dotenv():
        loguru.logger.info("Env variables loaded from .env file")
    else:
        loguru.logger.info(
            "No env variable loaded from .env file (file could be missing or empty)"
        )

    check_dot_env()
    loguru.logger.info("Required env variables loaded")

    app = flask.Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(DotEnvKey.DATABASE_URI.value)

    loguru.logger.info("Configure CORS")
    flask_cors.CORS(app)

    loguru.logger.info("Init database")
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

    loguru.logger.info("Init API routes")

    @app.route("/word/6/guess", methods=["POST"])
    def handle_player_guess_six_letters():
        return handle_player_guess(whitelist_6_letters)

    @app.route("/word/7/guess", methods=["POST"])
    def handle_player_guess_seven_letters():
        return handle_player_guess(whitelist_7_letters)

    @app.route("/word/8/guess", methods=["POST"])
    def handle_player_guess_eight_letters():
        return handle_player_guess(whitelist_8_letters)

    loguru.logger.info("App init is successful")
    return app
