#!/bin/bash

pipenv run python -m isort .
pipenv run python -m black .
pipenv run python -m ruff . --fix


