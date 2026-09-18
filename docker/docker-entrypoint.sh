#!/bin/sh

cd ./app

python manage.py migrate
python manage.py createsuperuser --username admin --email admin@inquests.ca --noinput

exec "$@"
