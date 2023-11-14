import json
import os

import flask
import pytest
from flask.testing import FlaskClient

from wordleapi.api import create_app, ErrorCode
from wordleapi.core import AVAILABLE_WORD_LENGTHS, ATTEMPT_REGEX, load_wordlefile
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


def get_correct_attempt_by_word_length(
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
                get_correct_attempt_by_word_length(
                    whitelist_6, whitelist_7, whitelist_8, word_length
                ),
                word_length,
            )
        commit()

    yield app.test_client()


@pytest.mark.parametrize("word_length", AVAILABLE_WORD_LENGTHS)
def test__when_attempt_is_correct__returns_http_200(
    app: flask.Flask,
    test_client: FlaskClient,
    whitelist_6: list[str],
    whitelist_7: list[str],
    whitelist_8: list[str],
    word_length: int,
):
    attempt = get_correct_attempt_by_word_length(
        whitelist_6, whitelist_7, whitelist_8, word_length
    )

    assert attempt in whitelist_6 or attempt in whitelist_7 or attempt in whitelist_8
    with app.app_context():
        today_word = (
            db.session.query(PlayedWord)
            .filter_by(word_length=word_length, date=now_yyyymmdd())
            .first()
            .word
        )
    assert attempt == today_word

    resp = test_client.post(
        path=f"/word/{word_length}/attempt", data={"attempt": attempt}
    )
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 200
    assert resp_json_data == {"success": True}


@pytest.mark.parametrize("word_length", AVAILABLE_WORD_LENGTHS)
def test__when_word_length_is_invalid__returns_http_422(
    test_client: FlaskClient, word_length: int
):
    attempt = "azert"
    assert len(attempt) != word_length

    resp = test_client.post(
        path=f"/word/{word_length}/attempt", data={"attempt": attempt}
    )
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data == {
        "code": ErrorCode.INVALID_ATTEMPT_LENGTH.value,
        "error_msg": f"'{attempt}' is not {word_length} letters long",
    }


@pytest.mark.parametrize("word_length", AVAILABLE_WORD_LENGTHS)
def test__when_attempt_is_empty__returns_http_422(
    test_client: FlaskClient, word_length: int
):
    attempt = ""
    assert len(attempt) == 0

    resp = test_client.post(
        path=f"/word/{word_length}/attempt", data={"attempt": attempt}
    )
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data == {
        "code": ErrorCode.EMPTY_ATTEMPT.value,
        "error_msg": "no attempt value submitted",
    }


@pytest.mark.parametrize(
    "word_length,attempt",
    (
        (6, "@zerty"),
        (6, "b4t3au"),
        (7, "ch4nvre"),
        (7, "etoile$"),
        (8, "et4p1ste"),
        (8, "sµrmµlot"),
    ),
)
def test__when_attempt_format_is_invalid__returns_http_422(
    test_client: FlaskClient, word_length: int, attempt: str
):
    resp = test_client.post(
        path=f"/word/{word_length}/attempt", data={"attempt": attempt}
    )
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data == {
        "code": ErrorCode.INVALID_FORMAT.value,
        "error_msg": f"'{attempt}' format is invalid (should match regex {ATTEMPT_REGEX})",
    }


@pytest.mark.parametrize(
    "word_length,attempt",
    (
        (6, "abcdef"),
        (7, "abcdefg"),
        (8, "abcdefgh"),
    ),
)
def test__when_attempt_not_in_whitelist__returns_http_422(
    test_client: FlaskClient, word_length: int, attempt: str
):
    resp = test_client.post(
        path=f"/word/{word_length}/attempt", data={"attempt": attempt}
    )
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data == {
        "code": ErrorCode.ATTEMPT_NOT_IN_WHITELIST.value,
        "error_msg": f"'{attempt}' is not in whitelist",
    }
