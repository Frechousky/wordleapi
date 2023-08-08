import datetime
import random

import pytz


def now() -> datetime.datetime:
    """
    Returns:
        Current date and time in Paris (France) as datetime.datetime object
    """
    return datetime.datetime.now(pytz.timezone("Europe/Paris"))


def now_yyyymmdd() -> str:
    """
    Returns:
        Current date in Paris (France) as "yyyyMMdd" string
        (e.g. on 2023/08/07 returns "20230807")
    """
    return now().strftime("%Y%m%d")


def strip_lower(s: str) -> str | None:
    """
    Args:
        s: string to process

    Returns:
        Stripped/lowercase string or None if s is None
    """
    if s is None:
        return None
    return s.strip().lower()


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
