#!/usr/bin/env bash
set -e

python manage.py migrate
python manage.py collectstatic --noinput
# python manage.py shell -c "from backend.create_superuser import run; run()"

gunicorn backend.wsgi:application --bind 0.0.0.0:10000