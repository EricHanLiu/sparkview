from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from user_management.models import Member
from .models import Notification
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
        return HttpResponse('You do not have permission to view this page.')
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
