#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py load_tags
python manage.py load_ingredients

exec gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
