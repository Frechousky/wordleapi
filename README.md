# wordleapi

API to process wordle game attempts.

## What is wordle ?

Wordle is a free online word game developed in 2021 by Josh Wardle.
This game is a direct adaptation of the American television game Lingo which asks you to guess a word
through several attempts, indicating for each of them the position of the well-placed and misplaced letters.
(source: Google)

## Requirements

- `python ^3.11`
- `pipenv`
- `make` (optional)

## Install

- `make install-deps` to install dependencies
- `make install-all-deps` to install dev depencies (optional)

## Usage

- `make` or `make run` to start wordle API server
- `make test`, `make test-unit`, `make test-inte` to run all tests, unit tests or integration tests
- See [Makefile](Makefile) for all available rules
