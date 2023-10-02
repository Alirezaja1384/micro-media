#!/usr/bin/env bash
set -e

# Add /app to PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

gunicorn_bind="${GUNICORN_BIND:-}"
gunicorn_certfile="${GUNICORN_CERT_FILE:-}"
gunicorn_keyfile="${GUNICORN_KEY_FILE:-}"

# Use default bind values if needed.
if [[ -z "$gunicorn_bind" ]]; then
    echo -n "> \$GUNICORN_BIND doesn't seem to be set. "

    # If both GUNICORN_CERT_FILE and GUNICORN_KEY_FILE are set
    if [[ -n "$gunicorn_certfile" && -n "$gunicorn_keyfile" ]]; then
        gunicorn_bind="0.0.0.0:443"
    # Otherwise:
    else
        gunicorn_bind="0.0.0.0:80"
    fi

    echo "Defaulting to $gunicorn_bind."
fi

echo "> Running alembic migrations" &&
    alembic upgrade head &&
    echo "> alembic migrations ran successfully."

# Seems like gunicorn ignores empty strings for certfile and keyfile,
#   So there should be no problem when certfile and keyfile are not set.
gunicorn \
    -k uvicorn.workers.UvicornWorker \
    -w "${GUNICORN_WORKERS:-1}" \
    -b "${gunicorn_bind}" \
    --certfile "$gunicorn_certfile" \
    --keyfile "$gunicorn_keyfile" \
    --forwarded-allow-ips="${GUNICORN_FORWARDED_ALLOW_IPS:-*}" \
    "${GUNICORN_APP:-micro_media.main:app}"
