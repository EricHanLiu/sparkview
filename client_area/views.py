from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from budget.models import Client

@login_required
def index(request):
    clients = Client.objects.all()

    context = {
        'clients' : clients,
        'user'    : request.user.get_profile
    }

    return render(request, 'client_area/clients.html', context)
