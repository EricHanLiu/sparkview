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
from . import other_views as other_views
from user_management import views as user_views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from user_management.views import members_single

from bloom.jwt_views import CustomTokenObtainPairView, CustomTokenVerifyView

urlpatterns = [
    url(r'^$', lviews.index, name='index'),
    url(r'^api/token/$', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^api/token/verify/$', CustomTokenVerifyView.as_view(), name='token_verify'),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^auth/login$', lviews.bloom_login, name='login'),
    url(r'^auth/logout$', lviews.bloom_logout, name='logout'),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r'^accounts/profile$', profile.view_profile, name='profile'),
    url(r'^search/', profile.search, name='search'),
    url(r'^users$', profile.user_list, name='user_list'),
    url(r'^users/add$', profile.create_user, name='create_user'),
    url(r'^users/delete$', profile.delete_user, name='delete_user'),
    url(r'^users/accounts/delete$', profile.remove_user_accounts, name='remove_user_accounts'),
    url(r'^password/$', profile.change_password, name='change_password'),
    url(r'^profile/delete$', profile.remove_acc_profile, name='delete_profile'),
    url(r'^dashboard$', members_single, name='dashboard'),
    url(r'^bing/', include('bing_dashboard.urls'), name='bing'),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^budget/', include('budget.urls', namespace='budget')),
    url(r'^tools/', include('tools.urls', namespace='tools')),
    url(r'^bloomapi/', include('api.urls', namespace='bloomapi')),
    url(r'^clients/', include('client_area.urls', namespace='client_area')),
    url(r'^user_management/', include('user_management.urls', namespace='user_management')),
    url(r'^notifications/', include('notifications.urls', namespace='notifications')),
    url(r'^reports/', include('reports.urls', namespace='reports')),
    url(r'^insights/', include('insights.urls', namespace='insights')),
    url(r'^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    url(r'^super/', admin.site.urls),
    url(r'^release_notes$', other_views.release_notes),
    url(r'^flower/', other_views.flower_view),
    url(r'^dashboard$', user_views.members_single),
    url(r'^profile$', user_views.profile, name='profile'),
    url(r'^profile/upload_image$', user_views.upload_image, name='upload_image'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Bloom Admin'
