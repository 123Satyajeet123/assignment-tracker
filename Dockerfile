FROM python:3.10-alpine

RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN mkdir /assignment_tracker
COPY ./assignment_tracker /assignment_tracker
WORKDIR /assignment_tracker
COPY ./scripts /scripts
RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/

RUN adduser -D admin
RUN chown -R admin:admin /vol 
RUN chmod -R 755 /vol/web

USER admin

# Collect static files and start uWSGI
#RUN python3 manage.py collectstatic --noinput

CMD ["entrypoint.sh"]