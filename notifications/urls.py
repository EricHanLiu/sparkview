from django.conf.urls import url, include
from notifications import views

app_name = "notifications"

urlpatterns = [
    url(r'^$', views.center, name='center'),
    url(r'^creator$', views.creator, name='creator')
]
