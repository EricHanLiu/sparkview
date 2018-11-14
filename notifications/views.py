from django.shortcuts import render

@login_required
def center(request):
    """
    Notification center
    Lists notifications to users
    """
