FROM python:3.13-alpine3.22

ARG USER=cleiton

RUN addgroup $USER && \
    adduser -D -G $USER $USER

USER "${USER}:${USER}"
VOLUME [ "/home/${USER}/.oci" ]

COPY ./src /srv/src
COPY ./pyproject.toml /srv/pyproject.toml
COPY ./poetry.lock /srv/poetry.lock

WORKDIR /srv

ENV PATH="/home/${USER}/.local/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false

RUN poetry install --without=dev --no-interaction --no-ansi --no-root

CMD [ "python", "-m", "src" ]