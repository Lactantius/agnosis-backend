#!/usr/bin/env sh
# Adapted from https://stackoverflow.com/a/57886655/6632828
set -e

. /venv/bin/activate

# while ! flask db upgrade
# do
#     echo "Retry..."
#     sleep 1
# done

exec gunicorn -c gunicorn.config.py wsgi:app
