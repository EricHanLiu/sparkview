#!/bin/bash

python manage.py makemigrations accounts
python manage.py makemigrations adwords_dashboard
python manage.py makemigrations bing_dashboard
python manage.py makemigrations facebook_dashboard
python manage.py makemigrations tools
python manage.py makemigrations budget


if [ $1 = "celery" ];
then
  celery worker -A bloom:celery_app --loglevel=info
else
  python manage.py runserver 0.0.0.0:8000
fi
