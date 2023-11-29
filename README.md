# wordleapi

API to process wordle game attempts.

## What is wordle ?

Wordle is a free online word game developed in 2021 by Josh Wardle.
This game is a direct adaptation of the American television game Lingo which asks you to guess a word
through several attempts, indicating for each of them the position of the well-placed and misplaced letters.
(source: Google)

## API

This API generates 3 words every day (resp 6, 7 and 8 letters long) and clients try to guess these words by submitting their attempt.

Submit a 6 letters length word attempt to guess today 6 letters word, same with 7 or 8 letters word.


### Examples

#### 1 - Valid attempt request/response (correct guess)</h4>

- Word to guess is 'ARBRES'
- `Request  => { "attempt": "ARBRES" }`
- `Response <= { "result": [0, 0, 0, 0, 0, 0] }`

Why is result [0, 0, 0, 0, 0, 0] ?

- All letters from player attempt ('ARBRES') are well-placed in today word ('ARBRES')
- Client guessed the word


#### 2 - Valid attempt request/response (incorrect guess)

- Word to guess is 'ARBRES'
- `Request  => { "attempt": "ARTERE" }`
- `Response <= { "result": [0, 0, 2, 1, 1, 2] }`

Why is result [0, 0, 2, 1, 1, 2] ?

- 'A' is well-placed in 'ARBRES' (0)
- 'R' is well-placed in 'ARBRES' (0)
- 'T' is not present in 'ARBRES' (2)
- 'E' is misplaced in 'ARBRES' (1)
- 'R' is misplaced in 'ARBRES' (1)
- 'E' is not present in 'ARBRES' (2) (there is only one E in 'ARBRES')
- Client did not guess the word (he may try again)


#### 3 - Invalid attempt request/response (attempt is too short)

- Word to guess is 'ARBRES'
- `Request  => { "attempt": "ARB" }`
- `Response <= { "code": 100, "error_msg": "Field 'attempt' is invalid or missing (String should have at least 6 characters)" }`


#### 4 - Invalid attempt request/response (attempt is not a whitelisted word)

- Some words are whitelisted, only these words may be the word to guess and only there word may be submitted by player (see [whitelist_files folder](whitelistfiles))
- 'ABCDEF' is not a whitelisted word
- `Request  => { "attempt": "ABCDEF" }`
- `Response <= { "code": 101, "error_msg": "'ABCDEF' is not in whitelist" }`


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
