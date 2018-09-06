from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from budget.models import Client
from user_management.models import Member

@login_required
def clients(request):
    member  = Member.objects.get(user=request.user)

    # Get all clients that this user is related to
    clients = Client.objects.filter(
                  Q(cm1=member) | Q(cm2=member) | Q(cm3=member) | Q(cmb=member) |
                  Q(am1=member) | Q(am2=member) | Q(am3=member) | Q(amb=member) |
                  Q(seo1=member) | Q(seo2=member) | Q(seo3=member) | Q(seob=member) |
                  Q(strat1=member) | Q(strat2=member) | Q(strat3=member) | Q(stratb=member)
              )

    user    = request.user
    member  = Member.objects.get(user=user)

    context = {
        'clients' : clients,
        'member'  : member
    }

    return render(request, 'client_area/clients.html', context)


@login_required
def clients_team(request):
    pass


@login_required
def clients_all(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')
    pass


@login_required
def clients_new(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')
    pass


@login_required
def clients_edit(request, id):
    client = Client.objects.get(id=id)

    context = {
        'client' : client
    }

    return render(request, 'client_area/client_edit.html', context)
