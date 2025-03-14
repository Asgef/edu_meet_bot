FROM python:3.13-slim
LABEL maintainer="asgefes1@gmail.com"

WORKDIR /app

ENV PYTHONDOWNTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1

RUN pip install --upgrade pip --no-cache-dir && \
    pip install poetry --no-cache-dir && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction

COPY . .


