#!/usr/bin/env bash
set -e
poetry install --with dev
pre-commit install
