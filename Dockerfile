FROM python:3.12-alpine

WORKDIR /opt/app
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN apk add make
RUN pip install -U pip && pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 20 && \
    poetry install --only main

COPY . .
RUN adduser bot -D && \
    chown -R bot:bot /opt/app && \
    chmod +x /opt/app/entrypoint.sh

USER bot

ENTRYPOINT [ "/opt/app/entrypoint.sh" ]
