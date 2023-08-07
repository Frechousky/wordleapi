#!/usr/bin/env python3
import enum
import os

import click


class DotEnvKey(enum.Enum):
    SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
    WORDLEFILE_6_LETTERS = "WORDLEFILE_6_LETTERS"
    WORDLEFILE_7_LETTERS = "WORDLEFILE_7_LETTERS"
    WORDLEFILE_8_LETTERS = "WORDLEFILE_8_LETTERS"


_DEFAULT_VALUES = {
    DotEnvKey.SQLALCHEMY_DATABASE_URI.value: "dialect+driver://username:password@host:port/database",
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


if __name__ == "__main__":
    _generate_default_dot_env()
