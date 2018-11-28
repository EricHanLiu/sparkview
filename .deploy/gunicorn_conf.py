##Configuration for gunicorn,
#this file is read from dir /var/run/gunicorn/
# more at http://docs.gunicorn.org/en/stable/settings.html

#CPU_CORES * 2 + 1
workers = 1

# user = "gunicorn"
# group = "www-data"

# bind = "unix:/var/run/gunicorn/gunicorn.sock"
bind = "0.0.0.0:8000"

# pidfile = "/var/run/gunicorn/pid"

worker_class = "aiohttp.worker.GunicornWebWorker"

threads = 6

#Maximum concurrent connections
worker_connections = 1000

#If set to 0 automatic restart is disabled
max_requests = 0

timeout = 60

# The number of seconds to wait for requests on a Keep-Alive connection.
keepalive = 2

# accesslog = "/var/log/gunicorn/access.log"
# errorlog = "/var/log/gunicorn/error.log"
<<<<<<< HEAD
loglevel = "info"
=======
loglevel = "debug"
>>>>>>> 0e143cf9c14dccca65e5438194eab96bbe46e69e
