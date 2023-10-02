##### Build image #####
FROM python:3.11-slim as build

# Set workdir
WORKDIR /app

# PIP
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

# System
ENV PATH="${PATH}:${POETRY_HOME}/bin"

# Copy poetry installation script
COPY ./install-poetry.py ./

# Install poetry 1.5.1
RUN python3 ./install-poetry.py --version 1.5.1

# Copy poetry.lock and pyproject.toml
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-ansi --only main

##### Production image #####
FROM python:3.11-slim as production

# Set workdir
WORKDIR /app

# Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Virtualenv
ENV VIRTUAL_ENV=/app/.venv

# Prepend virtualenv bin to PATH
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy project dependencies from build image
COPY --from=build /app/.venv ${VIRTUAL_ENV}

# Copy project files:
# - alembic.ini and entrypoint.sh
COPY ./alembic.ini ./entrypoint.sh ./
# - migrations directory
COPY ./migrations ./migrations
# - micro_media (Source code itself)
COPY ./micro_media ./micro_media

# When ssl cert and key are provided
EXPOSE 443
# When they're not ...
EXPOSE 80

CMD ["bash", "./entrypoint.sh"]
