#!/bin/bash

case "$SERVICE" in
   "web")
      python manage.py makemigrations
      python manage.py migrate
      python manage.py collectstatic --noinput

      gunicorn blog.wsgi:application --bind 0.0.0.0:8000
   ;;
    "celery_worker")
      celery -A blog worker -Q celery -n main_worker -l INFO --concurrency=30
   ;;
   "celery_beat")
      celery -A blog beat -l INFO
   ;;
esac
