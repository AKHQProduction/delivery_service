FROM docker.io/library/python:3.12-slim

ENV PATH="/venv/bin:$PATH" \
    VIRTUAL_ENV="/venv" \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/venv

COPY --from=ghcr.io/astral-sh/uv:0.8.13 /uv /uvx /usr/local/bin/

RUN set -eux; apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN uv venv /venv

WORKDIR /usr/src/app

# Install dependencies only (without dev and lint groups)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy the project files (will be overridden by volume mount in dev)
COPY . /usr/src/app

# Install project in editable mode
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --no-deps -e .
