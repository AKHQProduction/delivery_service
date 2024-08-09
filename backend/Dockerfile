FROM python:3.11-slim-buster

WORKDIR /app

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY . .

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

RUN poetry install