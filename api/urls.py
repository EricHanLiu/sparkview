from django.conf.urls import url
from django.contrib import admin
from api.views import ListAdwordsAccounts

app_name = "bloomapi"

urlpatterns = [
    url(r"^$", ListAdwordsAccounts.as_view(), name="listadwordsaccounts"),
]
