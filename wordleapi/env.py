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
            f"Missing env variable(s) {self.__missing_keys}. "
            f"Make sure to add these keys to .env file or as env variables before restarting app."
        )


class DotEnvKey(enum.Enum):
    DATABASE_URI = "DATABASE_URI"
    WORDLEFILE_6_LETTERS = "WORDLEFILE_6_LETTERS"
    WORDLEFILE_7_LETTERS = "WORDLEFILE_7_LETTERS"
    WORDLEFILE_8_LETTERS = "WORDLEFILE_8_LETTERS"


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
            loguru.logger.critical("Missing env variable '{}'", dek.value)
            missing_keys.append(dek.value)
        loguru.logger.debug("'{}' env variable loaded", dek.value)
    if missing_keys:
        raise MissingDotEnvKeyError(missing_keys)


_DEFAULT_VALUES = {
    DotEnvKey.DATABASE_URI.value: "dialect+driver://username:password@host:port/database",
    DotEnvKey.WORDLEFILE_6_LETTERS.value: "/path/to/wordlefile",
    DotEnvKey.WORDLEFILE_7_LETTERS.value: "/path/to/wordlefile",
    DotEnvKey.WORDLEFILE_8_LETTERS.value: "/path/to/wordlefile",
}


_INTE_VALUES = {
    DotEnvKey.DATABASE_URI.value: "sqlite:///wordleapi.db",
    DotEnvKey.WORDLEFILE_6_LETTERS.value: "wordlefiles/wordle_6_fr.txt",
    DotEnvKey.WORDLEFILE_7_LETTERS.value: "wordlefiles/wordle_7_fr.txt",
    DotEnvKey.WORDLEFILE_8_LETTERS.value: "wordlefiles/wordle_8_fr.txt",
}


def _generate_dot_env_file(outputdir: str, filename: str, kv: dict) -> None:
    """
    Generate .env file

    Args:
        outputdir: output dir to generate file
        filename: name of file to generate
        kv: key value pairs
    """
    if [key.name for key in DotEnvKey] != [key for key in kv.keys()]:
        error_msg = "invalid or missing dot env keys"
        loguru.logger.error(error_msg)
        raise click.ClickException(error_msg)
    with open(os.path.join(outputdir, filename), "w") as f:
        for key in kv:
            f.write(f"{key}={kv.get(key)}\n")


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--outputdir",
    "-o",
    default=".",
    help="Output directory to generate .env.default file",
)
def generate_default(outputdir: str):
    """
    Generate ".env.default" file with default values.
    """
    _generate_dot_env_file(outputdir, ".env.default", _DEFAULT_VALUES)


@cli.command()
@click.option(
    "--outputdir", "-o", default=".", help="Output directory to generate .env.inte file"
)
def generate_integration(outputdir: str):
    """
    Generate ".env.inte" file.
    """
    _generate_dot_env_file(outputdir, ".env.inte", _INTE_VALUES)


if __name__ == "__main__":
    cli()
