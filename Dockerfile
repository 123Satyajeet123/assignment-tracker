FROM python:3.9-alpine3.13

LABEL maintainer="satyajeet"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./assignment_tracker /assignment_tracker

WORKDIR /assignment_tracker

EXPOSE 8000

# Install build dependencies
RUN apk update && \
    apk add --no-cache build-base linux-headers && \
    apk add --no-cache postgresql-dev gcc python3-dev musl-dev

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --no-create-home app && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R app:app /vol && \
    chmod -R 755 /vol

# Remove build dependencies
RUN apk del build-base linux-headers

ENV PATH="/py/bin:$PATH"

USER app

