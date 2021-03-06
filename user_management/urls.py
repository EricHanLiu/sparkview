from django.conf.urls import url

from . import views

app_name = "user_management"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dashboard$', views.members_single, name='dashboard'),
    url(r'^profile$', views.redirect_to_members_single, name='redirect_to_members_single'),
    url(r'^members$', views.members, name='members'),
    url(r'^members/new$', views.new_member, name='new_member'),
    url(r'^members/(\d*)/dashboard$', views.member_dashboard, name='member_dashboard'),
    url(r'^members/(\d*)/edit$', views.edit_member, name='edit_member'),
    url(r'^members/(\d*)$', views.members_single, name='members_single'),
    url(r'^members/(\d*)/hours$', views.members_single_hours, name='members_single_hours'),
    url(r'^members/(\d*)/reports$', views.members_single_reports, name='members_single_reports'),
    url(r'^members/(\d*)/reports/update_date_status$', views.update_date_status, name='update_date_status'),
    url(r'^members/(\d*)/promos$', views.members_single_promos, name='members_single_promos'),
    url(r'^members/(\d*)/kpis$', views.members_single_kpis, name='members_single_kpis'),
    url(r'^members/(\d*)/timesheet$', views.members_single_timesheet, name='members_single_timesheet'),
    url(r'^members/(\d*)/performance$', views.performance, name='performance'),
    url(r'^members/(\d*)/input_hours$', views.input_hours_profile, name='input_hours'),
    url(r'^members/(\d*)/input_mandate$', views.input_mandate_profile, name='input_mandate'),
    url(r'^view_summary$', views.view_summary, name='view_summary'),
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
