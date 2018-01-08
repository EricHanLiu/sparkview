from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r"^$", views.adwords_accounts, name='adwords'),
    url(r"^bing/", views.bing_accounts, name='bing'),
]
