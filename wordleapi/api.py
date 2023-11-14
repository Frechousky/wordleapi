import enum
import os

import dotenv
import flask
import flask_cors
import loguru

from wordleapi.core import (
    ATTEMPT_REGEX,
    AttemptInvalidFormatError,
    AttemptIsEmptyError,
    AttemptNotInWhitelistError,
    InvalidAttemptLengthError,
    compute_attempt_result,
    get_today_word,
    load_wordlefile,
    validate_attempt,
)
from wordleapi.db.model import db
from wordleapi.env import DotEnvKey, check_dot_env
from wordleapi.utils import strip_lower


class ErrorCode(enum.Enum):
    INVALID_ATTEMPT_LENGTH = 100
    EMPTY_ATTEMPT = 101
    INVALID_FORMAT = 102
    ATTEMPT_NOT_IN_WHITELIST = 103


def build_error_response(code: ErrorCode, error_msg: str) -> dict:
    return {"code": code.value, "error_msg": error_msg}


def handle_player_attempt(whitelist: tuple[str]):
    attempt = strip_lower(flask.request.form.get("attempt", None))
    loguru.logger.debug("(attempt: '{}')", attempt)
    try:
        validate_attempt(attempt, whitelist)
    except InvalidAttemptLengthError as e:
        return (
            build_error_response(
                ErrorCode.INVALID_ATTEMPT_LENGTH,
                f"'{attempt}' is not {e.expected_length()} letters long",
            ),
            422,
        )
    except AttemptIsEmptyError:
        return (
            build_error_response(
                ErrorCode.EMPTY_ATTEMPT,
                "no attempt value submitted",
            ),
            422,
        )
    except AttemptInvalidFormatError:
        return (
            build_error_response(
                ErrorCode.INVALID_FORMAT,
                f"'{attempt}' format is invalid (should match regex {ATTEMPT_REGEX})",
            ),
            422,
        )
    except AttemptNotInWhitelistError:
        return (
            build_error_response(
                ErrorCode.ATTEMPT_NOT_IN_WHITELIST,
                f"'{attempt}' is not in whitelist",
            ),
            422,
        )
    word = get_today_word(whitelist)
    attempt_result = compute_attempt_result(attempt, word)

    if not attempt_result:
        return {"success": True}

    return {"success": False, "result": attempt_result}


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

    @app.route("/word/6/attempt", methods=["POST"])
    def handle_player_attempt_six_letters():
        return handle_player_attempt(whitelist_6_letters)

    @app.route("/word/7/attempt", methods=["POST"])
    def handle_player_attempt_seven_letters():
        return handle_player_attempt(whitelist_7_letters)

    @app.route("/word/8/attempt", methods=["POST"])
    def handle_player_attempt_eight_letters():
        return handle_player_attempt(whitelist_8_letters)

    loguru.logger.info("App init is successful")
    return app
