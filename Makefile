run:
	pipenv run gunicorn --bind 0.0.0.0:5000 wordleapi.wsgi:app

test:
	pipenv run pytest

test-unit:
	pipenv run pytest tests/unit

test-inte:
	pipenv run pytest tests/inte

install-deps:
	pipenv sync

install-all-deps:
	pipenv sync -d

update-deps:
	pipenv update

lint:
	pipenv run ruff check .

lint-fix:
	pipenv run ruff check . --fix

format:
	pipenv run ruff format .

dotenv-default:
	pipenv run wordleapi/env.py generate-default

dotenv-inte:
	pipenv run wordleapi/env.py generate-integration

dotenv: dotenv-default dotenv-inte

.PHONY: run test test-unit test-inte install-deps install-all-deps update-deps lint lint-fix format dotenv-default dotenv-inte dotenv
