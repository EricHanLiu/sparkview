from django.conf.urls import url, include
from notifications import views

app_name = "notifications"

urlpatterns = [
    url(r'^$', views.center, name='center'),
    url(r'^confirm$', views.confirm, name='confirm'),
    url(r'^cycle/confirm$', views.cycle_confirm, name='cycle_confirm')
]
