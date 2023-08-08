import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy

from wordleapi.utils import now_yyyymmdd

db = SQLAlchemy()


class PlayedWord(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    word = sa.Column(sa.String, unique=True, nullable=False)
    word_length = sa.Column(sa.Integer, nullable=False, index=True)
    date = sa.Column(sa.String, default=now_yyyymmdd())


def add_played_word(word: str, word_length: int):
    db.session.add(PlayedWord(word=word, word_length=word_length))


def delete_played_word_by_word_length(word_length: int):
    db.session.query(PlayedWord).filter_by(word_length=word_length).delete()


def get_first_played_word_by_word_length_and_date(
    word_length: int, _date: str
) -> PlayedWord | None:
    return (
        db.session.query(PlayedWord)
        .filter_by(word_length=word_length, date=_date)
        .first()
    )


def get_all_played_word_by_word_length(word_length: int) -> list[PlayedWord]:
    return db.session.query(PlayedWord).filter_by(word_length=word_length).all()


def commit():
    db.session.commit()
