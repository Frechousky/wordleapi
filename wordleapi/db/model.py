import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy

from wordleapi.utils import now_yyyymmdd

db = SQLAlchemy()


class WordHistory(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    word = sa.Column(sa.String, unique=True, nullable=False)
    word_length = sa.Column(sa.Integer, nullable=False, index=True)
    date = sa.Column(sa.String, default=now_yyyymmdd())


def add_word_history(word: str, word_length: int):
    db.session.add(WordHistory(word=word, word_length=word_length))


def delete_word_history_by_word_length(word_length: int):
    db.session.query(WordHistory).filter_by(word_length=word_length).delete()


def get_first_word_history_by_word_length_and_date(
    word_length: int, _date: str
) -> WordHistory | None:
    return (
        db.session.query(WordHistory)
        .filter_by(word_length=word_length, date=_date)
        .first()
    )


def get_all_word_history_by_word_length(word_length: int) -> list[WordHistory]:
    return db.session.query(WordHistory).filter_by(word_length=word_length).all()


def commit():
    db.session.commit()
