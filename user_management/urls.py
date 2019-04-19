from django.conf.urls import url

from . import views

app_name = "user_management"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile$', views.members_single, name='profile'),
    url(r'^members$', views.members, name='members'),
    url(r'^members/new$', views.new_member, name='new_member'),
    url(r'^members/(\d*)/dashboard$', views.member_dashboard, name='member_dashboard'),
    url(r'^members/(\d*)/edit$', views.edit_member, name='edit_member'),
    url(r'^members/(\d*)$', views.members_single, name='members_single'),
    url(r'^members/(\d*)/hours$', views.members_single_hours, name='members_single_hours'),
    url(r'^members/(\d*)/reports$', views.members_single_reports, name='members_single_reports'),
    url(r'^members/(\d*)/promos$', views.members_single_promos, name='members_single_promos'),
    url(r'^members/(\d*)/kpis$', views.members_single_kpis, name='members_single_kpis'),
    url(r'^members/(\d*)/timesheet$', views.members_single_timesheet, name='members_single_timesheet'),
    url(r'^members/(\d*)/skills$', views.members_single_skills, name='members_single_skills'),
    url(r'^members/(\d*)/oops$', views.member_oops, name='oops'),
    url(r'^members/(\d*)/high_fives$', views.member_high_fives, name='high_fives'),
    url(r'^members/training$', views.training_members, name='training_members'),
    url(r'^members/training/json$', views.training_members_json, name='training_members_json'),
    url(r'^teams$', views.teams, name='teams'),
    url(r'^teams/new$', views.new_team, name='new_team'),
    url(r'^skills$', views.skills, name='skills'),
    url(r'^skills/new$', views.skills_new, name='skills_new'),
    url(r'^backups$', views.backups, name='backups'),
    url(r'^backups/(\d*)$', views.backup_event, name='backup_event'),
    url(r'^add_training_hours$', views.add_training_hours, name='add_training_hours'),
    url(r'^late_onboard$', views.late_onboard, name='late_onboard')
]
