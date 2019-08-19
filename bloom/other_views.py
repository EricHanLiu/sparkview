from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse


@login_required
def release_notes(request):
    """
    We just have to write release notes in this html file
    :param request:
    :return:
    """
    return render(request, 'release_notes.html')


@user_passes_test(lambda u: u.is_staff and u.is_superuser)
def flower_view(request):
    """
    Passes the request back up to nginx for internal routing
    This will only work in production. Requires the following additional nginx configuration:
    =========================================
    location /flower-internal/static/ {
          internal;
          include  /etc/nginx/mime.types;
          sub_filter '/api' '/flower/api';
          sub_filter "'/monitor" "'/flower/monitor";
          sub_filter "'/worker" "'/flower/worker";
          sub_filter "'/'" "'/flower/'";
          sub_filter "'/dashboard" "'/flower/dashboard";
          sub_filter '"/update-dashboard"' '"/flower/update-dashboard"';
          sub_filter_types application/javascript;  # by default, sub_filter won't touch JS
          sub_filter_last_modified on;
          sub_filter_once off;
          rewrite ^/flower-internal/static/(.*)$ /$1 break;
          root <PATH_TO_PYTHON/VENV_DIR>/site-packages/flower/static/;
          add_header Content-Type text/css;
        }

        location /flower-internal/ {
            internal;
            rewrite ^/flower-internal/(.*)$ /$1 break;
            sub_filter '="/' '="/flower/';
            sub_filter_last_modified on;
            sub_filter_once off;

            proxy_pass http://127.0.0.1:5555;
            proxy_set_header Host $host;
        }
    =========================================
    From https://github.com/mher/flower/issues/762
    :param request:
    :return:
    """
    response = HttpResponse()
    path = request.get_full_path()
    path = path.replace('flower', 'flower-internal', 1)
    response['X-Accel-Redirect'] = path
    return response
