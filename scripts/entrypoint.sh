#!/bin/sh

set -e

# Collect static files
python manage.py collectstatic --noinput

# Start uWSGI with the configuration file
uwsgi --ini /assignment_tracker/uwsgi.ini
