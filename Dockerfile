FROM python:3.12-bookworm

RUN apt-get update && apt-get install -y \
  build-essential \
  libpq-dev \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /work

COPY . .

RUN poetry install

EXPOSE 80

RUN alembic upgrade head && \
  fastapi run --host 0.0.0.0 --port 80
