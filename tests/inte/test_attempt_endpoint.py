import json
import os
import re

import flask
import pytest
from flask.testing import FlaskClient

from wordleapi.api import create_app, ErrorCode
from wordleapi.core import (
    AVAILABLE_WORD_LENGTHS,
    load_whitelist_file,
    ATTEMPT_REGEX,
)
from wordleapi.db.model import db, add_played_word, commit
from wordleapi.env import DotEnvKey


@pytest.fixture()
def whitelist_6() -> tuple[str]:
    assert os.getenv(DotEnvKey.WHITELIST_FILE_6_LETTERS.value)
    return load_whitelist_file(os.getenv(DotEnvKey.WHITELIST_FILE_6_LETTERS.value))


@pytest.fixture()
def whitelist_7() -> tuple[str]:
    assert os.getenv(DotEnvKey.WHITELIST_FILE_7_LETTERS.value)
    return load_whitelist_file(os.getenv(DotEnvKey.WHITELIST_FILE_7_LETTERS.value))


@pytest.fixture()
def whitelist_8() -> tuple[str]:
    assert os.getenv(DotEnvKey.WHITELIST_FILE_8_LETTERS.value)
    return load_whitelist_file(os.getenv(DotEnvKey.WHITELIST_FILE_8_LETTERS.value))


@pytest.fixture()
def correct_word_6(whitelist_6) -> str:
    return whitelist_6[0]


@pytest.fixture()
def correct_word_7(whitelist_7) -> str:
    return whitelist_7[0]


@pytest.fixture()
def correct_word_8(whitelist_8) -> str:
    return whitelist_8[0]


@pytest.fixture()
def incorrect_word_6(whitelist_6) -> str:
    return whitelist_6[1]


@pytest.fixture()
def incorrect_word_7(whitelist_7) -> str:
    return whitelist_7[1]


@pytest.fixture()
def incorrect_word_8(whitelist_8) -> str:
    return whitelist_8[1]


@pytest.fixture()
def app() -> flask.Flask:
    app = create_app()
    app.testing = True
    yield app


@pytest.fixture()
def test_client(
    app: flask.Flask, correct_word_6: str, correct_word_7: str, correct_word_8: str
):
    # init database
    with app.app_context():
        db.drop_all()
        db.create_all()
        add_played_word(correct_word_6, 6)
        add_played_word(correct_word_7, 7)
        add_played_word(correct_word_8, 8)
        commit()
    yield app.test_client()


def test__when_attempt_is_correct__returns_http_200(
    test_client: FlaskClient,
    correct_word_6,
    correct_word_7,
    correct_word_8,
):
    attempts = [correct_word_6, correct_word_7, correct_word_8]
    for attempt in attempts:
        resp = test_client.post(path="/attempt", json={"attempt": attempt})
        resp_json_data = json.loads(resp.data)

        assert resp.status_code == 200
        assert resp_json_data == {"result": [0] * len(attempt)}


def test__when_attempt_is_incorrect__returns_http_200(
    test_client: FlaskClient,
    incorrect_word_6,
    incorrect_word_7,
    incorrect_word_8,
):
    incorrect_attempts = [incorrect_word_6, incorrect_word_7, incorrect_word_8]
    for attempt in incorrect_attempts:
        resp = test_client.post(path="/attempt", json={"attempt": attempt})
        resp_json_data = json.loads(resp.data)

        assert resp.status_code == 200
        assert resp_json_data.get("result") is not None
        assert len(resp_json_data.get("result")) == len(attempt)
        assert resp_json_data.get("result") != [0] * len(attempt)


def test__when_attempt_is_too_short__returns_http_422(test_client: FlaskClient):
    attempt = "azert"
    assert len(attempt) < min(AVAILABLE_WORD_LENGTHS)

    resp = test_client.post(path="/attempt", json={"attempt": attempt})
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data.get("code") == ErrorCode.INVALID_PAYLOAD.value
    assert (
        resp_json_data.get("error_msg")
        == f"Field 'attempt' is invalid or missing (String should have at least {min(AVAILABLE_WORD_LENGTHS)} characters)"
    )


def test__when_attempt_is_too_long__returns_http_422(test_client: FlaskClient):
    attempt = "azertyuiop"
    assert len(attempt) > max(AVAILABLE_WORD_LENGTHS)

    resp = test_client.post(path="/attempt", json={"attempt": attempt})
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data.get("code") == ErrorCode.INVALID_PAYLOAD.value
    assert (
        resp_json_data.get("error_msg")
        == f"Field 'attempt' is invalid or missing (String should have at most {max(AVAILABLE_WORD_LENGTHS)} characters)"
    )


def test__when_attempt_format_is_invalid__returns_http_422(test_client: FlaskClient):
    attempt = "@z3rty"
    assert re.match(ATTEMPT_REGEX, attempt) is None

    resp = test_client.post(path="/attempt", json={"attempt": attempt})
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data.get("code") == ErrorCode.INVALID_PAYLOAD.value
    assert (
        resp_json_data.get("error_msg")
        == f"Field 'attempt' is invalid or missing (String should match pattern '{ATTEMPT_REGEX}')"
    )


def test__when_body_is_empty__returns_http_422(test_client: FlaskClient):
    resp = test_client.post(path="/attempt")
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data.get("code") == ErrorCode.INVALID_PAYLOAD.value
    assert (
        resp_json_data.get("error_msg")
        == "Field 'attempt' is invalid or missing (Field required)"
    )


@pytest.mark.parametrize(
    "attempt",
    (
        "abcdef",
        "abcdefg",
        "abcdefgh",
    ),
)
def test__when_attempt_not_in_whitelist__returns_http_422(
    test_client: FlaskClient, attempt: str
):
    resp = test_client.post(path="/attempt", json={"attempt": attempt})
    resp_json_data = json.loads(resp.data)

    assert resp.status_code == 422
    assert resp_json_data == {
        "code": ErrorCode.ATTEMPT_NOT_IN_WHITELIST.value,
        "error_msg": f"'{attempt}' is not in whitelist",
    }
