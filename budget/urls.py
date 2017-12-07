from django.conf.urls import url, include
from django.contrib import admin
from budget import views

urlpatterns =[
    url(r"^$", views.index_budget, name="adwords"),
    url(r"^bing/", views.bing_budget, name="bing_budget"),
]