from django.conf.urls import url, include
from . import views

app_name = "accounts"

urlpatterns = [
    url(r"^$", views.adwords_accounts, name='adwords'),
    url(r"^bing/$", views.bing_accounts, name='bing'),
    url(r"^facebook/$", views.facebook_accounts, name='facebook'),
    url(r"^protected/$", views.change_protected, name='change_protected'),
    url(r"^bing/protected/$", views.change_protected, name='change_protected_bing'),
    url(r"^facebook/protected/$", views.change_protected, name='change_protected_facebook'),
]
