from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^members$', views.members, name='members'),
    url(r'^teams$', views.teams, name='teams'),
    url(r'^teams/new$', views.new_team, name='add_team'),
]
