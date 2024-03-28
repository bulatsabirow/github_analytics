FROM python:3.11
ENV PYTHONBUFFERED 1

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .
COPY alembic.ini .
COPY ./api ./api

RUN pip install poetry && poetry config virtualenvs.create false
RUN poetry install

COPY . .