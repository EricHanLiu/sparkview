"""bloom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import registration_views as lviews
from . import profile_views as profile
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r"^$", lviews.index, name='index'),
    url(r"^auth/login$", lviews.bloom_login, name='login'),
    url(r"^auth/logout$", lviews.bloom_logout, name='logout'),
    url(r"^auth/", include('social_django.urls', namespace='social')),
    url(r"^accounts/profile$", profile.view_profile, name='profile'),
    url(r"^users$", profile.user_list, name='user_list'),
    url(r"^users/add$", profile.create_user, name='create_user'),
    url(r"^users/delete$", profile.delete_user, name='delete_user'),
    url(r"^users/accounts/delete$", profile.remove_user_accounts, name='remove_user_accounts'),
    url(r'^password/$', profile.change_password, name='change_password'),
    url(r"^profile/delete$", profile.remove_acc_profile, name='delete_profile'),
    url(r"^dashboards/adwords/", include('adwords_dashboard.urls', namespace='adwords')),
    url(r"^dashboards/bing/", include('bing_dashboard.urls', namespace='bing')),
    url(r"^dashboards/facebook/", include('facebook_dashboard.urls', namespace='facebook')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^budget/', include('budget.urls', namespace='budget')),
    url(r'^tools/', include('tools.urls', namespace='tools')),
    url(r'^admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
