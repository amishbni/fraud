#!/bin/bash

case "$SERVICE" in
   "web")
      python manage.py makemigrations
      python manage.py migrate
      python manage.py collectstatic --noinput

      gunicorn blog.wsgi:application --bind 0.0.0.0:8000
   ;;
esac
