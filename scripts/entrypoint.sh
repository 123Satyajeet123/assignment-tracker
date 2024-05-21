#!/bin/sh

set -e

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start uWSGI with the configuration file

uwsgi --socket :8000 --workers 3 --master --enable-threads --module assignment_tracker.wsgi