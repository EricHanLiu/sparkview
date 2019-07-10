from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


@login_required
def insights(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('Bye')

    context = {

    }

    return render(request, 'insights/insights.html', context)
