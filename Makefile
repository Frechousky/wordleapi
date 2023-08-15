run:
	pipenv run gunicorn --bind 0.0.0.0:5000 wordleapi.wsgi:app

test:
	pipenv run pytest

install-deps:
	pipenv sync -d

update-deps:
	pipenv update

.PHONY: run test install-deps update-deps
