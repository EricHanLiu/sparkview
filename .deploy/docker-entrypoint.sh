#!/bin/bash

python manage.py makemigrations accounts
python manage.py makemigrations adwords_dashboard
python manage.py makemigrations bing_dashboard
python manage.py makemigrations facebook_dashboard
python manage.py makemigrations tools
python manage.py makemigrations client_area
python manage.py makemigrations budget
python manage.py makemigrations reports
python manage.py makemigrations user_management
python manage.py migrate




if [ $2 = "prod" ];
then
  echo "Running server in production"

  PSQL_NAME="bloom"
  PSQL_USER="bloom"
  PSQL_PASSWORD="Digital987x123"
  PSQL_HOST="localhost"
  if [ $1 = "celery" ];
  then
    echo "Starting celery"
    celery worker -A bloom:celery_app --loglevel=info --time-limit=300 --concurrency=8
  else 
    echo "Starting gunicorn"
    gunicorn bloom.wsgi --config ${PROJECT_DIR}/.deploy/gunicorn_conf.py
  fi

else
  echo "Running server in development"
  if [ $1 = "celery" ];
  then
    echo "Starting celery"
    celery worker -A bloom:celery_app --loglevel=info --time-limit=300 --concurrency=8
  else 
    echo "Starting django"
    python manage.py runserver 0.0.0.0:8000
  fi

fi