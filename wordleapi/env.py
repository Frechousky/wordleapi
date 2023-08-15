#!/usr/bin/env python3
import enum
import os

import click
import loguru


class MissingDotEnvKeyError(Exception):
    def __init__(self, missing_keys: list[str], *args, **kwargs):
        super().__init__(args, kwargs)
        self.__missing_keys = missing_keys

    def __str__(self):
        return (
            f"Missing keys {self.__missing_keys} from .env file. "
            f"Make sure to add these keys to .env file before restarting app."
        )


class DotEnvKey(enum.Enum):
    DATABASE_URI = "DATABASE_URI"
    WORDLEFILE_6_LETTERS = "WORDLEFILE_6_LETTERS"
    WORDLEFILE_7_LETTERS = "WORDLEFILE_7_LETTERS"
    WORDLEFILE_8_LETTERS = "WORDLEFILE_8_LETTERS"


_DEFAULT_VALUES = {
    DotEnvKey.DATABASE_URI.value: "dialect+driver://username:password@host:port/database",
    DotEnvKey.WORDLEFILE_6_LETTERS.value: "/path/to/wordlefile",
    DotEnvKey.WORDLEFILE_7_LETTERS.value: "/path/to/wordlefile",
    DotEnvKey.WORDLEFILE_8_LETTERS.value: "/path/to/wordlefile",
}


@click.command()
@click.option(
    "--outputdir", "-o", default=".", help="Output directory to generate .env file"
)
def _generate_default_dot_env(outputdir: str):
    """
    Generate ".env.default" file with default values.
    """
    with open(os.path.join(outputdir, ".env.default"), "w") as f:
        for k in _DEFAULT_VALUES.keys():
            f.write(f"{k}={_DEFAULT_VALUES.get(k)}\n")


def check_dot_env() -> None:
    """
    Check that all .env keys were read from .env files.

    Returns:
        None

    Raises:
        MissingDotEnvKeyError if any key/value pair is missing
    """
    missing_keys = []
    for dek in DotEnvKey:
        if not os.getenv(dek.value):
            loguru.logger.critical("Missing .env key/value pair '{}'", dek.value)
            missing_keys.append(dek.value)
        loguru.logger.debug("'{}' key/value pair loaded from .env", dek.value)
    if missing_keys:
        raise MissingDotEnvKeyError(missing_keys)


if __name__ == "__main__":
    _generate_default_dot_env()
