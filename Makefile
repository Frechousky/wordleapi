run:
	pipenv run gunicorn --bind 0.0.0.0:5000 wordleapi.wsgi:app

test:
	pipenv run pytest

unit-test:
	pipenv run pytest tests/unit

install-deps:
	pipenv sync

install-all-deps:
	pipenv sync -d

update-deps:
	pipenv update

.PHONY: run test unit-test install-deps install-all-deps update-deps
