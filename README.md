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
   
 