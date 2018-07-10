from django.conf.urls import url, include
from tools import views

urlpatterns = [
    url(r"^$", views.index_tools, name="index"),
    url(r"^labels/create$", views.create_labels, name="create_labels"),
    url(r"^labels/deassign$", views.deassign_labels, name="deassign_labels"),
    url(r"^labels/assign$", views.assign_labels, name="assing_labels"),
    url(r"^labels/get_campaigns$", views.get_campaigns, name="get_campaigns"),
    url(r"^labels/get_adgroups$", views.get_adgroups, name="get_adgroups"),
    url(r"^labels/get_labels$", views.get_labels, name="get_labels"),

]