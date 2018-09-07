from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^members$', views.members, name='members'),
    url(r'^members/new$', views.new_member, name='new_member'),
    url(r'^members/(\d*)/edit$', views.edit_member, name='edit_member'),
    url(r'^members/(\d*)$', views.members_single, name='members_single'),
    url(r'^members/training$', views.training_members, name='training_members'),
    url(r'^teams$', views.teams, name='teams'),
    url(r'^teams/new$', views.new_team, name='new_team'),
]
