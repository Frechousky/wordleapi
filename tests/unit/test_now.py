import datetime

import freezegun

from wordleapi.utils import now


@freezegun.freeze_time(datetime.datetime(1987, 8, 30, 12, 34, 56), tz_offset=-2)
def test_now__success():
    ret = now()

    assert ret.year == 1987, "year should be 1987"
    assert ret.month == 8, "month should be 8"
    assert ret.day == 30, "day should be 30"
    assert ret.hour == 12, "hour should be 12"
    assert ret.minute == 34, "minute should be 34"
    assert ret.second == 56, "second should be 56"
