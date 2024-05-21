FROM nginxinc/nginx-unprivileged:1-alpine

LABEL maintainer="sj"

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./entrypoint.sh /entrypoint.sh

ENV LISTEN_PORT=8080
ENV APP_HOST=assignment_tracker
ENV APP_PORT=8000

USER root

RUN mkdir -p /vol/static
RUN chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown -R nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /entrypoint.sh

VOLUME /vol/static

USER nginx

CMD ["/entrypoint.sh"]