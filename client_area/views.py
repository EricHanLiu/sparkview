from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q

from budget.models import Client
from user_management.models import Member, Team
from .models import ClientType, Industry, Language, Service, ClientContact
from .forms import NewClientForm


@login_required
def accounts(request):
    member  = Member.objects.get(user=request.user)
    accounts = Client.objects.filter(
                  Q(cm1=member) | Q(cm2=member) | Q(cm3=member) | Q(cmb=member) |
                  Q(am1=member) | Q(am2=member) | Q(am3=member) | Q(amb=member) |
                  Q(seo1=member) | Q(seo2=member) | Q(seo3=member) | Q(seob=member) |
                  Q(strat1=member) | Q(strat2=member) | Q(strat3=member) | Q(stratb=member)
              )

    context = {
        'member'   : member,
        'accounts' : accounts
    }

    return render(request, 'client_area/accounts.html', context)


@login_required
def accounts_team(request):
    pass


@login_required
def accounts_all(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    accounts = Client.objects.all()

    context = {
        'accounts' : accounts
    }

    return render(request, 'client_area/accounts_all.html', context)


@login_required
def account_new(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    if (request.method == 'GET'):
        teams        = Team.objects.all()
        client_types = ClientType.objects.all()
        industries   = Industry.objects.all()
        languages    = Language.objects.all()
        members      = Member.objects.all()
        services     = Service.objects.all()
        tiers        = [1, 2, 3]

        context = {
            'teams'        : teams,
            'client_types' : client_types,
            'industries'   : industries,
            'languages'    : languages,
            'members'      : members,
            'services'     : services,
            'tiers'        : tiers
        }

        return render(request, 'client_area/account_new.html', context)
    elif (request.method == 'POST'):
        formData = {
            'client_name'   : request.POST.get('client_name'),
            'budget'        : request.POST.get('budget'),
            'team'          : request.POST.get('team'),
            'client_type'   : request.POST.get('client_type'),
            'industry'      : request.POST.get('industry'),
            'language'      : request.POST.get('language'),
            'contact_email' : request.POST.get('contact_email'),
            'contact_name'  : request.POST.get('contact_name'),
            'tier'          : request.POST.get('tier'),
            'sold_by'       : request.POST.get('sold_by'),
            'services'      : request.POST.get('services'),
            'status'        : request.POST.get('status'),
            'client_grade'  : request.POST.get('client_grade'),
        }

        form = NewClientForm(formData)

        if form.is_valid():
            cleanedInputs = form.clean()

            # Make a contact object
            contactInfo = ClientContact(name=cleanedInputs['contact_name'], email=cleanedInputs['contact_email'])

            client = Client.objects.create(
                        client_name=cleanedInputs['client_name'],
                        budget=cleanedInputs['budget'],
                        clientType=cleanedInputs['client_type'],
                        industry=cleanedInputs['industry'],
                        soldBy=cleanedInputs['sold_by']
                    )

            contactInfo.save()

            # set teams
            teams = [cleanedInputs['team']]
            client.team.set(teams)

            # set languages
            languages = [cleanedInputs['language']]
            client.language.set(languages)

            # set contact info
            contacts = [contactInfo]
            client.contactInfo.set(contacts)

            return redirect('/accounts/all')
        else:
            return HttpResponse('Invalid form entries')
    else:
        return HttpResponse('You are at the wrong place')


@login_required
def account_edit(request, id):
    account = Client.objects.get(id=id)

    context = {
        'account' : account
    }

    return render(request, 'client_area/account_edit.html', context)


@login_required
def account_single(request, id):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    account = Client.objects.get(id=id)
    members = Member.objects.all()

    context = {
        'account' : account,
        'members' : members
    }

    return render(request, 'client_area/account_single.html', context)


@login_required
def account_assign_members(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    account_id = request.POST.get('account_id')
    account    = Client.objects.get(id=account_id)

    # There may be a better way to handle this form
    # This is terrible boilerplate
    # CMS
    cm1_id = request.POST.get('cm1-assign')
    if (cm1_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=cm1_id)
    account.cm1 = member

    cm2_id = request.POST.get('cm2-assign')
    if (cm2_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=cm2_id)
    account.cm2 = member

    cm3_id = request.POST.get('cm3-assign')
    if (cm3_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=cm3_id)
    account.cm3 = member

    cmb_id = request.POST.get('cmb-assign')
    if (cmb_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=cmb_id)
    account.cmb = member

    # AMs
    am1_id = request.POST.get('am1-assign')
    if (am1_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=am1_id)
    account.am1 = member

    am2_id = request.POST.get('am2-assign')
    if (am2_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=am2_id)
    account.am2 = member

    am3_id = request.POST.get('am3-assign')
    if (am3_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=am3_id)
    account.am3 = member

    amb_id = request.POST.get('amb-assign')
    if (amb_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=amb_id)
    account.amb = member

    # SEO
    seo1_id = request.POST.get('seo1-assign')
    if (seo1_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=seo1_id)
    account.seo1 = member

    seo2_id = request.POST.get('seo2-assign')
    if (seo2_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=seo2_id)
    account.seo2 = member

    seo3_id = request.POST.get('seo3-assign')
    if (seo3_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=seo3_id)
    account.seo3 = member

    seob_id = request.POST.get('seob-assign')
    if (seob_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=seob_id)
    account.seob = member

    # Strat
    srtat1_id = request.POST.get('strat1-assign')
    if (srtat1_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=srtat1_id)
    account.strat1 = member

    srtat2_id = request.POST.get('strat2-assign')
    if (srtat2_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=srtat2_id)
    account.strat2 = member

    srtat3_id = request.POST.get('strat3-assign')
    if (srtat3_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=srtat3_id)
    account.strat3 = member

    srtatb_id = request.POST.get('stratb-assign')
    if (srtatb_id == '0'):
        member = None
    else:
        member = Member.objects.get(id=srtatb_id)
    account.stratb = member

    account.save()

    print(account.am1.user.first_name)

    return redirect('/clients/accounts/' + str(account.id))
