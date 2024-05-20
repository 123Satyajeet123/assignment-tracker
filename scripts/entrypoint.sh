#!/bin/sh

set -e

# Collect static files
python manage.py collectstatic --noinput

# Start uWSGI
uwsgi --socket :8000 --master --processes 2 --threads 2 --module assignment_tracker.wsgi
