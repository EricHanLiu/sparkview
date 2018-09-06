from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.clients, name='clients'),
    url(r'^team$', views.clients_team, name='clients_team'),
    url(r'^all$', views.clients_all, name='clients_all'),
    url(r'^new$', views.clients_new, name='clients_new'),
    url(r'^(\d)/edit$', views.clients_edit, name='clients_edit')
]
