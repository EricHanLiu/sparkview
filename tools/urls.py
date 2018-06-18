from django.conf.urls import url, include
from tools import views

urlpatterns = [
    url(r"^$", views.index_tools, name="index"),
    url(r"^labels/create$", views.create_labels, name="create_labels"),
    url(r"^labels/deassign$", views.deassign_labels, name="deassign_labels"),
    url(r"^labels/assign$", views.assign_labels, name="assing_labels"),

]