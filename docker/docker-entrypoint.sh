#!/bin/sh

cd ./app

python manage.py migrate
python manage.py createsuperuser --noinput

exec "$@"
