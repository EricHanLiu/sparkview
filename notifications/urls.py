from django.conf.urls import url, include
from notifications import views

app_name = "notifications"

urlpatterns = [
    url(r'^$', views.get_notifications, name="get_notifications")
]
