# Adapted from https://stackoverflow.com/a/57886655/6632828
FROM python:3.10-alpine as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.2.0

RUN apk add --no-cache gcc musl-dev
RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN . /venv/bin/activate && poetry install --no-dev --no-root
#RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

COPY . .

RUN . /venv/bin/activate && poetry build
#RUN poetry build && /venv/bin/pip install dist/*.whl

FROM base as final

# RUN apk add --no-cache ?
COPY --from=builder /venv /venv
COPY --from=builder /app/dist .
COPY docker-entrypoint.sh wsgi.py ./

RUN . /venv/bin/activate && pip install *.whl

EXPOSE 5000

ENTRYPOINT ["app/docker-entrypoint.sh"]
