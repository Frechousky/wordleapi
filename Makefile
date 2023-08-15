run:
	poetry run gunicorn --bind 0.0.0.0:5000 wordleapi.wsgi:app

test:
	poetry run pytest

install-deps:
	poetry install

update-deps:
	poetry update

build:
	poetry build

.PHONY: run test install-deps update-deps build
