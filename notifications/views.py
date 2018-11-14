from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from user_management.models import Member


@login_required
def center(request):
    """
    Notification center
    Lists notifications to users
    """
    member = Member.objects.get(user=request.user)
    notifications = member.unread_notifications

    context = {
        'notifications' : notifications
    }

    return render(request, 'notifications/center.html', context)


@login_required
def creator(request):
    """
    Page to create notifications (recurring or one time)
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page.')
    return HttpResponse('Creator')


@login_required
def create(request):
    """
    Creates recurring or one time notification
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page.')
    return HttpResponse('Create')
