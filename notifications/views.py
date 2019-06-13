from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from user_management.models import Member
from .models import Notification, Todo
from client_area.models import PhaseTaskAssignment, LifecycleEvent
import datetime


@login_required
def center(request):
    """
    Notification center
    Lists notifications to users
    """
    member = Member.objects.get(user=request.user)
    notifications = member.unread_notifications

    context = {
        'notifications': notifications
    }

    return render(request, 'notifications/center.html', context)


@login_required
def create(request):
    """
    Creates recurring or one time notification
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page.')
    return HttpResponse('Create')


@login_required
def confirm(request):
    """
    Confirms that a notification has been acknowleged by a user
    """
    member = Member.objects.get(user=request.user)
    notification_id = request.POST.get('notification_id')
    notification = Notification.objects.get(id=notification_id)
    if notification.member != member:
        return HttpResponse('This is not your notification')
    elif notification.confirmed:
        return HttpResponse('This notification is already confirmed')

    notification.confirmed = True
    notification.confirmed_at = datetime.datetime.now()
    notification.save()

    return HttpResponse('Success')


@login_required
def cycle_confirm(request):
    """
    Confirms a "90 days of awesome" task
    """
    member = Member.objects.get(user=request.user)
    task_id = request.POST.get('task_id')
    task = PhaseTaskAssignment.objects.get(id=task_id)
    flagged = request.POST.get('flagged') == 'True'

    bc_link = request.POST.get('bc_link')
    if bc_link == '' or bc_link is None:
        return HttpResponse('You must enter a basecamp link to flag or confirm a task.')

    if task.complete:
        return HttpResponse('This task is already confirmed!')

    account = task.account

    if flagged:
        task.flagged = True
        if not account.star_flag:
            account.star_flag = True
            account.flagged_bc_link = bc_link
            account.save()

    task.complete = True
    task.bc_link = bc_link
    task.completed = datetime.datetime.now()
    task.completed_by = member
    task.save()

    # also check off the TODO
    today = datetime.date.today()
    todo = Todo.objects.get(date_created=today, phase_task_id=task.id)
    todo.completed = True
    todo.save()

    event_description = member.user.get_full_name() + ' completed the task: ' + task.task.message + '.'
    notes = 'Basecamp link: ' + task.bc_link
    lc_event = LifecycleEvent.objects.create(account=account, type=7, description=event_description,
                                             phase=account.phase,
                                             phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                             bing_active=account.has_bing,
                                             facebook_active=account.has_fb,
                                             adwords_active=account.has_adwords,
                                             monthly_budget=account.current_budget,
                                             spend=account.current_spend, notes=notes)

    lc_event.members.set(account.assigned_members_array)
    lc_event.save()

    return redirect('/user_management/profile')
