FROM python:3.11-rc-buster AS builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.11-rc-slim-buster AS runtime

ENV VIRTUAL_ENV=/usr/src/app/.venv \
    PATH="/usr/src/app/.venv/bin:$PATH"
ENV PYTHONPATH=/usr/src/app/src

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src ./usr/src/app/src
#COPY alembic.ini ./usr/src/app