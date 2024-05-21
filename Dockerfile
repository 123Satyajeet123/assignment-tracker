FROM python:3.9-alpine3.13

LABEL maintainer="sj"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./assignment_tracker /assignment_tracker
COPY ./scripts /scripts

WORKDIR /assignment_tracker
EXPOSE 8000

# Install build dependencies

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache --virtual .tmp-deps \
    build-base postgresql-dev gcc musl-dev linux-headers && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --no-create-home app && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R app:app /vol && \
    chmod -R 755 /vol && \
    chmod +x /scripts/*

# Remove build dependencies
RUN apk del build-base linux-headers

ENV PATH="/scripts:/py/bin:$PATH"

USER app

CMD ["entrypoint.sh"]