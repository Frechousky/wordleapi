import datetime
import random

import pytz


def now_yyyymmdd() -> str:
    """
    Returns:
        Current date in Paris (France) as "yyyyMMdd" string
        (e.g. on 2023/08/07 returns "20230807")
    """
    return datetime.datetime.now(pytz.timezone("Europe/Paris")).strftime("%Y%m%d")


def pick_random_element(seq: list | tuple):
    """
    Picks a random element from a tuple or list.

    Args:
        seq: sequence to pick a random element from

    Returns:
        Random element from seq
    """
    random.seed()
    return seq[random.randrange(len(seq))]
