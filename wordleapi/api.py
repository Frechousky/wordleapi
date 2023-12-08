import enum
import os

import dotenv
import flask
import flask_openapi3
import flask_cors
import loguru
import pydantic
import werkzeug

from wordleapi.core import (
    ATTEMPT_REGEX,
    compute_attempt_result,
    get_today_word,
    load_whitelist_file,
    AVAILABLE_WORD_LENGTHS,
    LetterPositionStatus as LPS,
)
from wordleapi.db.model import db
from wordleapi.env import DotEnvKey, check_dot_env


class AttemptRequest(pydantic.BaseModel):
    """Player attempt request to process."""

    attempt: str = pydantic.Field(
        title="Player attempt",
        description="Player attempt to process.",
        pattern=ATTEMPT_REGEX,
        min_length=min(AVAILABLE_WORD_LENGTHS),
        max_length=max(AVAILABLE_WORD_LENGTHS),
    )

    model_config = {
        "openapi_extra": {
            "examples": {
                "req-1": {
                    "summary": "1 - Valid attempt request (correct guess)",
                    "value": {"attempt": "ARBRES"},
                },
                "req-2": {
                    "summary": "2 - Valid attempt request (incorrect guess)",
                    "value": {"attempt": "ARTERE"},
                },
                "req-3": {
                    "summary": "3 - Invalid attempt request (attempt is too short)",
                    "value": {"attempt": "ARB"},
                },
                "req-4": {
                    "summary": "4 - Invalid attempt request (attempt is not a whitelisted word)",
                    "value": {"attempt": "ABCDEF"},
                },
            }
        }
    }


class AttemptResponse(pydantic.BaseModel):
    """Player attempt result response."""

    result: list[LPS] = pydantic.Field(
        title="Attempt result",
        description=f"Contains position status for each letter from request attempt:"
        f"{LPS.__doc__}",
    )

    model_config = {
        "openapi_extra": {
            "examples": {
                "resp-1": {
                    "summary": "1 - Valid attempt response (correct guess)",
                    "value": {"result": [0, 0, 0, 0, 0, 0]},
                },
                "resp-2": {
                    "summary": "2 - Valid attempt response (incorrect guess)",
                    "value": {"result": [0, 0, 2, 1, 1, 2]},
                },
            }
        }
    }


class ErrorCode(enum.Enum):
    """
    100 (invalid payload),
    101 (attempt not in whitelist)
    102 (HTTP method not allowed)
    """

    INVALID_PAYLOAD = 100
    ATTEMPT_NOT_IN_WHITELIST = 101
    METHOD_NOT_ALLOWED = 102


class ErrorResponse(pydantic.BaseModel):
    """API error response."""

    code: ErrorCode = pydantic.Field(
        title="API error code",
        description="Computer friendly error code:" f"{ErrorCode.__doc__}",
    )
    error_msg: str = pydantic.Field(
        title="API error message",
        description="Human readable descriptive error message",
    )

    model_config = {
        "openapi_extra": {
            "examples": {
                "resp-3": {
                    "summary": "3 - Invalid attempt response (attempt is too short)",
                    "value": {
                        "code": 100,
                        "error_msg": f"Field 'attempt' is invalid or missing (String should have at least {min(AVAILABLE_WORD_LENGTHS)} characters)",
                    },
                },
                "resp-4": {
                    "summary": "4 - Invalid attempt response (attempt is not a whitelisted word)",
                    "value": {"code": 101, "error_msg": "'ABCDEF' is not in whitelist"},
                },
                "resp-5": {
                    "summary": "5 - Invalid HTTP method",
                    "value": {
                        "code": 102,
                        "error_msg": "Method not allowed, accepted methods are ['OPTIONS', 'POST']",
                    },
                },
            },
        }
    }


def _build_json_response(data: str, status_code: int) -> flask.Response:
    response = flask.make_response(data)
    response.headers["Content-Type"] = "application/json"
    response.status_code = status_code
    return response


def make_validation_error_response(e: pydantic.ValidationError) -> flask.Response:
    """
    Create a Flask response for a validation error.

    Args:
        e: The ValidationError object containing the details of the error.

    Returns:
        FlaskResponse: A Flask Response object with the JSON representation of the error.
    """
    return _build_json_response(
        ErrorResponse(
            code=ErrorCode.INVALID_PAYLOAD,
            error_msg=f"Field '{e.errors()[0].get('loc')[0]}' is invalid or missing ({e.errors()[0].get('msg')})",
        ).model_dump_json(),
        422,
    )


def create_app() -> flask_openapi3.OpenAPI:
    """Create flask app"""
    loguru.logger.info("Init app")

    # ENV variables loading/checking
    if dotenv.load_dotenv():
        loguru.logger.info("Env variables loaded from .env file")
    else:
        loguru.logger.info(
            "No env variable loaded from .env file (file could be missing or empty)"
        )
    check_dot_env()
    loguru.logger.info("Required env variables loaded")

    app = flask_openapi3.OpenAPI(
        __name__, validation_error_callback=make_validation_error_response
    )

    # CORS configuration
    loguru.logger.info("Configure CORS")
    flask_cors.CORS(app)

    # DATABASE initialization
    loguru.logger.info("Init database")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(DotEnvKey.DATABASE_URI.value)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # WHITELIST FILES loading (contains playable words)
    whitelists_by_word_length = {
        6: load_whitelist_file(os.getenv(DotEnvKey.WHITELIST_FILE_6_LETTERS.value)),
        7: load_whitelist_file(os.getenv(DotEnvKey.WHITELIST_FILE_7_LETTERS.value)),
        8: load_whitelist_file(os.getenv(DotEnvKey.WHITELIST_FILE_8_LETTERS.value)),
    }
    if list(whitelists_by_word_length.keys()) != AVAILABLE_WORD_LENGTHS:
        loguru.logger.error(
            "Invalid whitelist by word length dict, make sure there is one whitelist file for each available word length"
        )
        return None

    # ROUTES
    loguru.logger.info("Init API route")

    @app.post(
        "/attempt",
        responses={200: AttemptResponse, 422: ErrorResponse, 405: ErrorResponse},
    )
    def post_attempt(body: AttemptRequest):
        """
        Process player attempt

        This is the wordle API endpoint.


        <h3>What is wordle ?</h3>

        Wordle is a free online word game developed in 2021 by Josh Wardle.
        This game is a direct adaptation of the American television game Lingo which asks you to guess a word
        through several attempts, indicating for each of them the position of the well-placed and misplaced letters.
        (source: Google)

        This API generates 3 words every day (resp 6, 7 and 8 letters long) and clients try to guess these words by submitting their attempt.
        Submit a 6 letters length word attempt to guess today 6 letters word, same with 7 or 8 letters word.


        <h3>Examples</h3>

        <h4>1 - Valid attempt request/response (correct guess)</h4>

        Word to guess is 'ARBRES'
        <pre>
        Request  => { "attempt": "ARBRES" }
        Response <= { "result": [0, 0, 0, 0, 0, 0] }
        </pre>
        Why is result [0, 0, 0, 0, 0, 0] ?
        All letters from player attempt ('ARBRES') are well-placed in today word ('ARBRES')
        => Client guessed the word


        <h4>2 - Valid attempt request/response (incorrect guess)</h4>

        Word to guess is 'ARBRES'
        <pre>
        Request  => { "attempt": "ARTERE" }<
        Response <= { "result": [0, 0, 2, 1, 1, 2] }
        </pre>
        Why is result [0, 0, 2, 1, 1, 2] ?
        'A' is well-placed in 'ARBRES' (0)
        'R' is well-placed in 'ARBRES' (0)
        'T' is not present in 'ARBRES' (2)
        'E' is misplaced in 'ARBRES' (1)
        'R' is misplaced in 'ARBRES' (1)
        'E' is not present in 'ARBRES' (2) (there is only one E in 'ARBRES')
        => Client did not guess the word (he may try again)


        <h4>3 - Invalid attempt request/response (attempt is too short)</h4>

        Word to guess is 'ARBRES'
        <pre>
        Request  => { "attempt": "ARB" }
        Response <= { "code": 100, "error_msg": "Field 'attempt' is invalid or missing (String should have at least 6 characters)" }
        </pre>


        <h4>4 - Invalid attempt request/response (attempt is not a whitelisted word)</h4>

        Some words are whitelisted, only these words may be the word to guess and only there word may be submitted by player.
        'ABCDEF' is not a whitelisted word
        <pre>
        Request  => { "attempt": "ABCDEF" }
        Response <= { "code": 101, "error_msg": "'ABCDEF' is not in whitelist" }
        </pre>
        """
        whitelist = whitelists_by_word_length.get(len(body.attempt))
        attempt = body.attempt.lower()
        if attempt not in whitelist:
            return _build_json_response(
                ErrorResponse(
                    code=ErrorCode.ATTEMPT_NOT_IN_WHITELIST,
                    error_msg=f"'{body.attempt}' is not in whitelist",
                ).model_dump_json(),
                422,
            )
        word = get_today_word(whitelist)
        attempt_result = compute_attempt_result(attempt, word)
        return _build_json_response(
            AttemptResponse(result=attempt_result).model_dump_json(),
            200,
        )

    @app.errorhandler(405)
    def handle_405(e: werkzeug.exceptions.MethodNotAllowed):
        return _build_json_response(
            ErrorResponse(
                code=ErrorCode.METHOD_NOT_ALLOWED,
                error_msg=f"Method not allowed, accepted methods are {e.valid_methods}",
            ).model_dump_json(),
            405,
        )

    loguru.logger.info("App init is successful")
    return app
