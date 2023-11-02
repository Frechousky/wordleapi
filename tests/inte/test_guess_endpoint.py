import json
import os

import flask
import pytest
from flask.testing import FlaskClient

from wordleapi.api import create_app, ErrorCode
from wordleapi.core import AVAILABLE_WORD_LENGTHS, GUESS_REGEX, load_wordlefile
from wordleapi.db.model import db, add_played_word, commit, PlayedWord
from wordleapi.env import DotEnvKey
from wordleapi.utils import now_yyyymmdd


@pytest.fixture
def whitelist_6() -> list[str]:
    assert os.getenv(DotEnvKey.WORDLEFILE_6_LETTERS.value)
    return load_wordlefile(os.getenv(DotEnvKey.WORDLEFILE_6_LETTERS.value))


@pytest.fixture
def whitelist_7() -> list[str]:
    assert os.getenv(DotEnvKey.WORDLEFILE_7_LETTERS.value)
    return load_wordlefile(os.getenv(DotEnvKey.WORDLEFILE_7_LETTERS.value))


@pytest.fixture
def whitelist_8() -> list[str]:
    assert os.getenv(DotEnvKey.WORDLEFILE_8_LETTERS.value)
    return load_wordlefile(os.getenv(DotEnvKey.WORDLEFILE_8_LETTERS.value))


def get_correct_guess_by_word_length(
    whitelist_6: list[str],
    whitelist_7: list[str],
    whitelist_8: list[str],
    word_length: int,
):
    if word_length == 6:
        return whitelist_6[0]
    if word_length == 7:
        return whitelist_7[0]
    if word_length == 8:
        return whitelist_8[0]


@pytest.fixture
def app() -> flask.Flask:
    app = create_app()
    app.testing = True
    yield app


@pytest.fixture
def test_client(
    app: flask.Flask,
    whitelist_6: list[str],
    whitelist_7: list[str],
    whitelist_8: list[str],
):
    with app.app_context():
        db.drop_all()
        db.create_all()
        for word_length in AVAILABLE_WORD_LENGTHS:
            add_played_word(
                get_correct_guess_by_word_length(
                    whitelist_6, whitelist_7, whitelist_8, word_length
                ),
                word_length,
            )
        commit()

    yield app.test_client()


@pytest.mark.parametrize("word_length", AVAILABLE_WORD_LENGTHS)
def test__when_guess_is_correct__returns_http_200(
    app: flask.Flask,
    test_client: FlaskClient,
    whitelist_6: list[str],
    whitelist_7: list[str],
    whitelist_8: list[str],
    word_length: int,
):
    guess = get_correct_guess_by_word_length(
        whitelist_6, whitelist_7, whitelist_8, word_length
    )

    assert guess in whitelist_6 or guess in whitelist_7 or guess in whitelist_8
    with app.app_context():
        today_word = (
            db.session.query(PlayedWord)
            .filter_by(word_length=word_length, date=now_yyyymmdd())
            .first()
            .word
        )
    assert guess == today_word

    resp = test_client.post(path=f"/word/{word_length}/guess", data={"guess": guess})
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 200
    assert resp_json_data == {"success": True}


@pytest.mark.parametrize("word_length", AVAILABLE_WORD_LENGTHS)
def test__when_word_length_is_invalid__returns_http_422(
    test_client: FlaskClient, word_length: int
):
    guess = "azert"
    assert len(guess) != word_length

    resp = test_client.post(path=f"/word/{word_length}/guess", data={"guess": guess})
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data == {
        "code": ErrorCode.HPG_INVALID_GUESS_LENGTH.value,
        "error_msg": f"'{guess}' is not {word_length} letters long",
    }


@pytest.mark.parametrize("word_length", AVAILABLE_WORD_LENGTHS)
def test__when_guess_is_empty__returns_http_422(
    test_client: FlaskClient, word_length: int
):
    guess = ""
    assert len(guess) == 0

    resp = test_client.post(path=f"/word/{word_length}/guess", data={"guess": guess})
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data == {
        "code": ErrorCode.HPG_EMPTY_GUESS.value,
        "error_msg": "no guess value submitted",
    }


@pytest.mark.parametrize(
    "word_length,guess",
    (
        (6, "@zerty"),
        (6, "b4t3au"),
        (7, "ch4nvre"),
        (7, "etoile$"),
        (8, "et4p1ste"),
        (8, "sµrmµlot"),
    ),
)
def test__when_guess_format_is_invalid__returns_http_422(
    test_client: FlaskClient, word_length: int, guess: str
):
    resp = test_client.post(path=f"/word/{word_length}/guess", data={"guess": guess})
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data == {
        "code": ErrorCode.HPG_INVALID_FORMAT.value,
        "error_msg": f"'{guess}' format is invalid (should match regex {GUESS_REGEX})",
    }


@pytest.mark.parametrize(
    "word_length,guess",
    (
        (6, "abcdef"),
        (7, "abcdefg"),
        (8, "abcdefgh"),
    ),
)
def test__when_guess_not_in_whitelist__returns_http_422(
    test_client: FlaskClient, word_length: int, guess: str
):
    resp = test_client.post(path=f"/word/{word_length}/guess", data={"guess": guess})
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data == {
        "code": ErrorCode.HPG_GUESS_NOT_IN_WHITELIST.value,
        "error_msg": f"'{guess}' is not in whitelist",
    }
