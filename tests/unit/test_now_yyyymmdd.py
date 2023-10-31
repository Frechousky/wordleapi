import freezegun

from wordleapi.utils import now_yyyymmdd


@freezegun.freeze_time("1987-08-30")
def test_now_yyyymmdd__success():
    assert now_yyyymmdd() == "19870830"
