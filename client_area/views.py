from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models import Q
import calendar, datetime

from budget.models import Client
from user_management.models import Member, Team
from .models import ClientType, Industry, Language, Service, ClientContact, AccountHourRecord, AccountChanges, ParentClient, ManagementFeeInterval, ManagementFeesStructure
from .forms import NewClientForm


@login_required
def accounts(request):
    member  = Member.objects.get(user=request.user)
    accounts = member.accounts

    backupAccounts = Client.objects.filter(Q(cmb=member) | Q(amb=member) | Q(seob=member) | Q(stratb=member))

    statusBadges = ['info', 'success', 'warning', 'danger']


    context = {
        'member'         : member,
        'backupAccounts' : backupAccounts,
        'statusBadges' : statusBadges,
        'accounts'       : accounts
    }

    return render(request, 'client_area/accounts.html', context)


@login_required
def accounts_team(request):
    member   = Member.objects.get(user=request.user)
    teams    = member.team

    accounts = {}
    for team in teams.all():
        accounts[team.id] = Client.objects.filter(team=team)

    statusBadges = ['info', 'success', 'warning', 'danger']

    context = {
        'member'   : member,
        'statusBadges' : statusBadges,
        'teams'    : teams,
        'accounts' : accounts
    }

    return render(request, 'client_area/accounts_team.html', context)


@login_required
def accounts_all(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    accounts = Client.objects.all()

    statusBadges = ['info', 'success', 'warning', 'danger']

    context = {
        'statusBadges' : statusBadges,
        'accounts'     : accounts
    }

    return render(request, 'client_area/accounts_all.html', context)


@login_required
def account_new(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    if (request.method == 'GET'):
        teams        = Team.objects.all()
        client_types = ClientType.objects.all()
        clients      = ParentClient.objects.all()
        industries   = Industry.objects.all()
        languages    = Language.objects.all()
        members      = Member.objects.all()
        services     = Service.objects.all()
        tiers        = [1, 2, 3]

        context = {
            'teams'        : teams,
            'client_types' : client_types,
            'clients'      : clients,
            'industries'   : industries,
            'languages'    : languages,
            'members'      : members,
            'services'     : services,
            'tiers'        : tiers
        }

        return render(request, 'client_area/account_new.html', context)
    elif (request.method == 'POST'):

        formData = {
            'account_name'   : request.POST.get('account_name'),
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
        }

        form = NewClientForm(formData)

        if form.is_valid():
            cleanedInputs = form.clean()

            # Make a contact object
            contactInfo = ClientContact(name=cleanedInputs['contact_name'], email=cleanedInputs['contact_email'])

            # Get existing client
            if (not int(request.POST.get('existing_client')) == 0):
                client = ParentClient.objects.get(id=request.POST.get('existing_client'))
            else:
                client = ParentClient.objects.create(name=request.POST.get('client_name'))

            account = Client.objects.create(
                        client_name=cleanedInputs['account_name'],
                        clientType=cleanedInputs['client_type'],
                        industry=cleanedInputs['industry'],
                        soldBy=cleanedInputs['sold_by']
                    )

            contactInfo.save()

            # set parent client
            account.parentClient = client

            # set teams
            # teams = [cleanedInputs['team']]
            # account.team.set(teams)

            # set languages
            languages = [cleanedInputs['language']]
            account.language.set(languages)

            # set PPC services
            services = [cleanedInputs['services']]
            account.services.set(services)

            # set contact info
            contacts = [contactInfo]
            account.contactInfo.set(contacts)

            # Make management fee structure
            # This is temporary
            feeType = request.POST.get('fee-type1')
            fee     = request.POST.get('fee1')
            initFee = request.POST.get('setup-fee')

            feeInterval = ManagementFeeInterval.objects.create(feeStyle=feeType, fee=fee, lowerBound=0, upperBound=99999999)
            feeInterval.save()
            feeStructure = ManagementFeesStructure.objects.create(initialFee=initFee)
            feeStructure.feeStructure.set([feeInterval])

            feeStructure.save()

            account.managementFee = feeStructure

            # Check if we sold SEO and/or CRO
            if (request.POST.get('seo_check')):
                account.has_seo = True
                account.seo_hours = request.POST.get('seo_hours')
            if (request.POST.get('cro_check')):
                account.has_cro = True
                account.cro_hours = request.POST.get('cro_hours')

            account.has_gts = True
            account.has_budget = True

            account.save()

            return redirect('/clients/accounts/all')
        else:
            return HttpResponse('Invalid form entries')
    else:
        return HttpResponse('You are at the wrong place')


@login_required
def account_edit_temp(request, id):
    member = Member.objects.get(user=request.user)
    if (not request.user.is_staff and not member.has_account(id) and not member.teams_have_accounts(id)):
        return HttpResponse('You do not have permission to view this page')

    if (request.method == 'GET'):
        account = Client.objects.get(id=id)

        context = {
            'account' : account
        }

        return render(request, 'client_area/account_edit_temp.html', context)
    elif (request.method == 'POST'):
        account = get_object_or_404(Client, id=id)

        account_name = request.POST.get('account_name')
        seo_hours = request.POST.get('seo_hours')
        cro_hours = request.POST.get('cro_hours')

        fee_override = request.POST.get('fee_override')
        hours_override = request.POST.get('hours_override')

        if (account.client_name != account_name):
            # Audit log There
            account.client_name = account_name

        if (seo_hours != '' and float(seo_hours) != 0.0):
            account.has_seo = True
            account.seo_hours = seo_hours
        else:
            account.has_seo = False
            account.seo_hours = 0.0

        if (cro_hours != '' and float(cro_hours) != 0.0):
            account.has_cro = True
            account.cro_hours = cro_hours
        else:
            account.has_cro = False
            account.cro_hours = 0.0

        if (fee_override != 'None'):
            account.management_fee_override = float(fee_override)

        if (request.user.is_staff):
            if (hours_override != 'None'):
                account.allocated_ppc_override = float(hours_override)

        account.save()

        return redirect('/clients/accounts/' + str(account.id))


@login_required
def account_edit(request, id):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    if (request.method == 'GET'):
        account      = Client.objects.get(id=id)
        teams        = Team.objects.all()
        client_types = ClientType.objects.all()
        industries   = Industry.objects.all()
        languages    = Language.objects.all()
        members      = Member.objects.all()
        services     = Service.objects.all()
        statuses     = Client._meta.get_field('status').choices
        tiers        = [1, 2, 3]

        context = {
            'account'      : account,
            'teams'        : teams,
            'client_types' : client_types,
            'industries'   : industries,
            'languages'    : languages,
            'members'      : members,
            'statuses'     : statuses,
            'services'     : services,
            'tiers'        : tiers
        }

        return render(request, 'client_area/account_edit.html', context)
    elif (request.method == 'POST'):
        account = get_object_or_404(Client, id=id)

        member = Member.objects.get(user=request.user)

        formData = {
            'account_name'  : request.POST.get('account_name'),
            'team'          : request.POST.get('team'),
            'client_type'   : request.POST.get('client_type'),
            'industry'      : request.POST.get('industry'),
            'language'      : request.POST.get('language'),
            'contact_email' : request.POST.get('contact_email'),
            'contact_name'  : request.POST.get('contact_name'),
            'sold_by'       : request.POST.get('soldby'),
            'services'      : request.POST.get('services'),
            'status'        : request.POST.get('status'),
        }

        form = NewClientForm(formData)

        if form.is_valid():
            cleanedInputs = form.clean()

            # Make a contact object
            contactInfo = ClientContact(name=cleanedInputs['contact_name'], email=cleanedInputs['contact_email'])

            # Bad boilerplate
            # Change this eventually
            if (account.client_name != cleanedInputs['account_name']):
                AccountChanges.objects.create(account=account, member=member, changeField='account_name', changedFrom=account.client_name, changedTo=cleanedInputs['account_name'])
                account.client_name = cleanedInputs['account_name']

            if (account.clientType != cleanedInputs['client_type']):
                AccountChanges.objects.create(account=account, member=member, changeField='client_type', changedFrom=account.clientType.name, changedTo=cleanedInputs['client_type'])
                account.clientType = cleanedInputs['client_type']

            if (account.industry != cleanedInputs['industry']):
                AccountChanges.objects.create(account=account, member=member, changeField='industry', changedFrom=account.industry.name, changedTo=cleanedInputs['industry'])
                account.industry = cleanedInputs['industry']

            if (account.soldBy != cleanedInputs['sold_by']):
                AccountChanges.objects.create(account=account, member=member, changeField='sold_by', changedFrom=account.soldBy.user.first_name + ' ' + account.soldBy.user.last_name, changedTo=cleanedInputs['sold_by'])
                account.soldBy = cleanedInputs['sold_by']

            if (account.status != cleanedInputs['status']):
                AccountChanges.objects.create(account=account, member=member, changeField='status', changedFrom=account.status, changedTo=cleanedInputs['status'])
                account.status = cleanedInputs['status']

            contactInfo.save()

            # set teams
            teams = [cleanedInputs['team']]
            account.team.set(teams)

            # set languages
            languages = [cleanedInputs['language']]
            account.language.set(languages)

            # set contact info
            contacts = [contactInfo]
            account.contactInfo.set(contacts)

            account.save()

            return redirect('/clients/accounts/' + str(account.id))
        else:
            return HttpResponse('Invalid form entries')
    else:
        return HttpResponse('You are at the wrong place')


@login_required
def account_single(request, id):
    member = Member.objects.get(user=request.user)
    if (not request.user.is_staff and not member.has_account(id) and not member.teams_have_accounts(id)):
        return HttpResponse('You do not have permission to view this page')

    account = Client.objects.get(id=id)
    members = Member.objects.all()
    changes = AccountChanges.objects.filter(account=account)

    # Get hours this month for this account
    now   = datetime.datetime.now()
    month = now.month
    year  = now.year
    accountHoursThisMonth = AccountHourRecord.objects.filter(account=account, month=month, year=year)

    accountsHoursThisMonthByMember = AccountHourRecord.objects.filter(account=account, month=month, year=year).values('member', 'month', 'year').annotate(Sum('hours'))

    statusBadges = ['info', 'success', 'warning', 'danger']

    context = {
        'account'               : account,
        'members'               : members,
        'accountHoursMember'    : accountsHoursThisMonthByMember,
        'changes'               : changes,
        'accountHoursThisMonth' : accountHoursThisMonth,
        'statusBadges'          : statusBadges
    }

    return render(request, 'client_area/account_single.html', context)


@login_required
def account_assign_members(request):
    member = Member.objects.get(user=request.user)
    account_id = request.POST.get('account_id')
    if (not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id)):
        return HttpResponse('You do not have permission to view this page')

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

    return redirect('/clients/accounts/' + str(account.id))


@login_required
def add_hours_to_account(request):

    if (request.method == 'GET'):
        member   = Member.objects.get(user=request.user)
        accounts = Client.objects.filter(
                      Q(cm1=member) | Q(cm2=member) | Q(cm3=member) | Q(cmb=member) |
                      Q(am1=member) | Q(am2=member) | Q(am3=member) | Q(amb=member) |
                      Q(seo1=member) | Q(seo2=member) | Q(seo3=member) | Q(seob=member) |
                      Q(strat1=member) | Q(strat2=member) | Q(strat3=member) | Q(stratb=member)
                  )

        months = [(str(i), calendar.month_name[i]) for i in range(1,13)]
        years  = [2018, 2019]

        now = datetime.datetime.now()
        monthnow = now.month

        context = {
            'member'   : member,
            'accounts' : accounts,
            'months'   : months,
            'monthnow' : monthnow,
            'years'    : years
        }

        return render(request, 'client_area/insert_hours.html', context)

    elif (request.method == 'POST'):
        account_id = request.POST.get('account_id')
        account    = Client.objects.get(id=account_id)
        member = Member.objects.get(user=request.user)
        if (not request.user.is_staff and not member.has_account(account_id)):
            return HttpResponse('You do not have permission to add hours to this account')
        member     = Member.objects.get(user=request.user)
        hours      = request.POST.get('hours')
        month      = request.POST.get('month')
        year       = request.POST.get('year')

        AccountHourRecord.objects.create(member=member, account=account, hours=hours, month=month, year=year)

        return redirect('/user_management/profile')


@login_required
def account_allocate_percentages(request):
    member = Member.objects.get(user=request.user)
    account_id = request.POST.get('account_id')
    account    = Client.objects.get(id=account_id)
    if (not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id)):
        return HttpResponse('You do not have permission to view this page')

    # There may be a better way to handle this form
    # This is boilerplate
    # CMs
    cm1percent = request.POST.get('cm1-percent')
    if (cm1percent == None or cm1percent == ''):
        cm1percent = 0
    account.cm1percent = cm1percent

    cm2percent = request.POST.get('cm2-percent')
    if (cm2percent == None or cm2percent == ''):
        cm2percent = 0
    account.cm2percent = cm2percent

    cm3percent = request.POST.get('cm3-percent')
    if (cm3percent == None or cm3percent == ''):
        cm3percent = 0
    account.cm3percent = cm3percent

    am1percent = request.POST.get('am1-percent')
    if (am1percent == None or am1percent == ''):
        am1percent = 0
    account.am1percent = am1percent

    am2percent = request.POST.get('am2-percent')
    if (am2percent == None or am2percent == ''):
        am2percent = 0
    account.am2percent = am2percent

    am3percent = request.POST.get('am3-percent')
    if (am3percent == None or am3percent == ''):
        am3percent = 0
    account.am3percent = am3percent

    seo1percent = request.POST.get('seo1-percent')
    if (seo1percent == None or seo1percent == ''):
        seo1percent = 0
    account.seo1percent = seo1percent

    seo2percent = request.POST.get('seo2-percent')
    if (seo2percent == None or seo2percent == ''):
        seo2percent = 0
    account.seo2percent = seo2percent

    seo3percent = request.POST.get('seo3-percent')
    if (seo3percent == None or seo3percent == ''):
        seo3percent = 0
    account.seo3percent = seo3percent

    strat1percent = request.POST.get('strat1-percent')
    if (strat1percent == None or strat1percent == ''):
        strat1percent = 0
    account.strat1percent = strat1percent

    strat2percent = request.POST.get('strat2-percent')
    if (strat2percent == None or strat2percent == ''):
        strat2percent = 0
    account.strat2percent = strat2percent

    strat3percent = request.POST.get('strat3-percent')
    if (strat3percent == None or strat3percent == ''):
        strat3percent = 0
    account.strat3percent = strat3percent

    account.save()

    return redirect('/clients/accounts/' + str(account.id))