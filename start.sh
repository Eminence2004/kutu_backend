#!/bin/bash
cd /app/kutu_core
python manage.py migrate --noinput
exec gunicorn --bind 0.0.0.0:8000 kutu_core.wsgi:application
