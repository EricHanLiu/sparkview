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


#### Current SparkView prod Setup
 - SparkView is running as a docker container (the web service)
 - Crons are handled by crontab on Sam's user
 - The directory where the project is checked out that's handling the crons is `/home/sam/bloom-master`
 - To re-setup the crons do: `cd /home/sam/bloom-master`, `source env/bin/activate` (or whatever the env folder is, might be named differently), `python manage.py crontab remove`, `python manage.py crontab add`. This should re add the crons. If not, see `django-crontab` docs.
 - To see the docker services running, do `sudo docker ps`, the web service is the one running the actual web app.
 - The server is nginx, it reverse proxies to the docker container (`0.0.0.0:8000`, I think)
 - The crons run scripts that spawn celery tasks
 - These tasks are queued up in a redis server
 
 
#### Things to check if SparkView is giving 502 errors
 ##### Check if the server is full
  - ssh into the server (log into GCP to give someone access, a dev should be able to figure this out, also we only have one server running so that's the one they need to ssh into), type `df` (mainly check if the `var` folder or `tmp` folders are overflowing)
  - If the server is full, a number of problems can occur that result in SparkView running slowly or failing completely.
  - First things to look for are `/tmp/suds` files or similar. These should be able to be deleted without consequence.
  - Another option is to delete some old docker images with  `sudo docker rmi <IMAGE_ID>`. You can see image IDs with `sudo docker images`. Maybe delete an old one from the `hyperdigitalteam/bloom` repository.


#### Things to check if SparkView is giving 500 errors
 - Check if the action can be done in the admin backend
 
 
## Bing auth
 - Bing gives us a file that seems to be used like a private key for auth
 - That file is located at `/bing_dashboards/bing_creds`
 - If that file doesn't exist, you can do `$ cp bing_dashboards/bing_creds_prod bing_dashboards/bing_creds` in production

 
## How to get Bing credentials
 - Go to the path `/bing/auth/get_url` and follow the link
 - Login with the dev@makeitbloom.com account
 - This will make/update the file `/bing_dashboards/bing_creds`
   - If on local, you may have to slightly alter the redirect URL (possibly remove `/dashboards` and possibly switch `localhost` to `127.0.0.1`)
 
 
##  When updating cron tasks
 - Restart celery `sudo sh /etc/init.d/celeryd restart`
 
## Deployment Checklist
 - Pull the latest version
 - Make sure `DEBUG = False` in `bloom/settings.py`
 - Set DB settings to prod values in `bloom/settings.py` 
 - Migrate DB to latest schema `python manage.py migrate`
 - Make sure bing credentials are in place `cp bing_dashboards/bing_creds_prod bing_dashboards/bing_creds`
 - If new cron jobs, run `python manage.py crontab add` (must be from `sam` user, may need to be run several times)
 - Restart gunicorn `sudo systemctl restart gunicorn`
 - Restart celery `sudo systemctl restart celeryd.service`
 - Optionally test `python manage.py test`
 
## Old Deployment Checklist

 - Pull latest version
 - Make sure `DEBUG = False` in `bloom/settings.py`
 - Set DB settings to prod values in `bloom/settings.py`
 - Build docker container with `sudo docker image build .`
 - Restart celery `sudo sh /etc/init.d/celeryd restart`
 - Make sure bing credentials are in place `cp bing_dashboards/bing_creds_prod bing_dashboards/bing_creds`
 - Update crontab `python manage.py crontab add` (Must be from `sam` user, you may have to run this multiple times until there is no error)
 - Tag the newest version's container
   * Get the container id with `sudo docker images` (should look something like `1d2846775d6b`)
   * Set the docker version with `sudo docker tag {{ id }} makeitbloom/sparkview:{{ v }}` where `{{ id }}` is the id from the previous step, and `{{ v }}` is the next number (just increment previous build number). Note this is different from the SparkView version.
   * Push the latest version to docker repo with `sudo docker push makeitbloom/sparkview:{{ v }}`
 - Update the software to the newest container with `sudo docker service update --image makeitbloom/sparkview:{{ v }} bloom_web`
 
 
 ## Scheduled Task Setup (as of August 2019)
 
  - Now using celery beat (using django admin panel to schedule the tasks)
  - Celery running as a daemon, same as before
  - Now using flower as a monitoring service (https://github.com/mher/flower/issues/762)
  
 ### Suds Jurko fix
 
  - We use a library called suds-jurko
  - Sometimes, this causes massive files to be created in `/tmp/suds`. If this happens, see https://bitbucket.org/jurko/suds/issues/126/millions-of-temp-files-eating-my-hard
  - Here is the fix, in case it ever gets deleted:
  
    For reference I am using python 3.4 and suds-jurko (0.6) installed using pip3.

    Had the same issue and the most expedient fix for me was to manually patch the file: site-packages/suds/reader.py
    
    add to imports:
    
    `import hashlib`
    
    change this line:
    
    `h = abs(hash(name))`
    
    to:
    
    `h = hashlib.md5(name.encode()).hexdigest()`
    
    For me, this fixed the issue. Now there are only 6 cache files and they haven't grown or added in months.