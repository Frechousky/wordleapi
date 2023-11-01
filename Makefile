run:
	pipenv run gunicorn --bind 0.0.0.0:5000 wordleapi.wsgi:app

test:
	pipenv run pytest

test-unit:
	pipenv run pytest tests/unit

install-deps:
	pipenv sync

install-all-deps:
	pipenv sync -d

update-deps:
	pipenv update

lint:
	pipenv run ruff check .

format:
	pipenv run ruff format .

.PHONY: run test test-unit install-deps install-all-deps update-deps lint format
