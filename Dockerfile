FROM python:3.12-bookworm

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
  build-essential \
  libpq-dev \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /work

COPY . .

RUN python -m venv .venv && \
  source .venv/bin/activate && \
  /root/.local/bin/poetry install

EXPOSE 80


CMD ["/bin/bash", "-c","/work/.venv/bin/alembic upgrade head && \
     mkdir -p ~/uploads ~/models && \
     /work/.venv/bin/fastapi run --host 0.0.0.0 --port 80"]
