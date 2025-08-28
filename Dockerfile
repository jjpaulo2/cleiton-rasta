FROM python:3.13-alpine3.22

COPY ./src /srv/src
COPY ./pyproject.toml /srv/pyproject.toml
COPY ./poetry.lock /srv/poetry.lock

WORKDIR /srv

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

CMD [ "python", "-m", "src" ]