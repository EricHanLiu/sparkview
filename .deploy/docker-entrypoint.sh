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
python manage.py makemigrations django_celery_results
python manage.py migrate

if [ -z $2 ] || [ -z $1 ]
then
  echo "Mode and app is not set"
  echo "Run the script like this sh ${0} [app_name] [mode]"
  exit 0
fi

MODE=$2
APP=$1

if [ $MODE = "prod" ];
then
  echo "Running server in production"

  export PSQL_NAME="bloom"
  export PSQL_USER="bloom"
  export PSQL_PASSWORD="Digital987x123"
  export PSQL_HOST="bloom-database"
  if [ $APP = "celery" ];
  then
    echo "Starting celery"
    celery worker -A bloom:celery_app --loglevel=info --time-limit=300 --concurrency=8
  else
    echo "Starting gunicorn"
    gunicorn bloom.wsgi --config ${PROJECT_DIR}/.deploy/gunicorn_conf.py
  fi

else
  echo "Running server in development"
  if [ $APP = "celery" ];
  then
    echo "Starting celery"
    celery worker -A bloom:celery_app --loglevel=info --time-limit=300 --concurrency=8
  else
    echo "Starting django"
    python manage.py runserver 0.0.0.0:8000
  fi

fi
