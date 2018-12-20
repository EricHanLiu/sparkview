# Bloom Platform by HyperDigital.io


## Development environment setup

- Setup development environment

  - Install PostgreSQL
  - Configure PostgreSQL - make sure the user you create matches the one from settings.py - see link below

  - https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04
  - Install Redis Server with the settings from settings.py
  - Clone project from Git
  - pip install requirements from requirements.txt
  - Apply migrations
  - Run the app

- Deployment
  - ssh into app.mibhub.com
  - pull the latest version into /home/nonono/bloom
  - activate envirnment (source bloomenv/bin/activate)
  - apply the migrations
  - if static files(js, css, etc...) have been modified :
    - sudo chown -R youruser:youruser /var/www/bloom
    - python manage.py collectstatic
    - sudo chown -R root:root /var/www/bloom
  - restart gunicorn (sudo service gunicorn restart)

## If things go wrong when Sam is gone


- Current SparkView prod Setup
 - SparkView is running as a docker container (the web service)
 - Crons are handled by crontab on Sam's user
 - The directory where the project is checked out that's handling the crons is `/home/sam/bloom-master`
 - To re-setup the crons do: `cd /home/sam/bloom-master`, `source env/bin/activate` (or whatever the env folder is, might be named differently), `python manage.py crontab remove`, `python manage.py crontab add`. This should re add the crons. If not, see `django-crontab` docs.
 - To see the docker services running, do `sudo docker ps`, the web service is the one running the actual web app.
 - The server is nginx, it reverse proxies to the docker container (`0.0.0.0:8000`, I think)

- Things to check if SparkView is giving 502 errors
 - Check if the server is full
  - ssh into the server (log into GCP to give someone access, a dev should be able to figure this out, also we only have one server running so that's the one they need to ssh into), type `df` (mainly check if the `var` folder or `tmp` folders are overflowing)
  - If the server is full, a number of problems can occur that result in SparkView running slowly or failing completely.
  - First things to look for are `tmp/suds` files or similar. These should be able to be deleted without consequence.
  - Another option is to delete some old docker images with  `sudo docker rmi <IMAGE_ID>`. You can see image IDs with `sudo docker images`. Maybe delete an old one from the `hyperdigitalteam/bloom` repository.

- Things to check if SparkView is giving 500 errors
 - Check if the action can be done in the admin backend
