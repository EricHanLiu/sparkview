from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.db.models import Q
from django.utils import timezone
import calendar
import datetime

from budget.models import Client
from user_management.models import Member, Team, BackupPeriod, Backup
from notifications.models import Notification
from .models import Promo, MonthlyReport, ClientType, Industry, Language, Service, ClientContact, AccountHourRecord, \
    AccountChanges, ParentClient, ManagementFeeInterval, ManagementFeesStructure, OnboardingStepAssignment, \
    OnboardingStep, OnboardingTaskAssignment, OnboardingTask, LifecycleEvent, SalesProfile
from .forms import NewClientForm


@login_required
def accounts(request):
    member = Member.objects.get(user=request.user)
    accounts = member.accounts

    now = datetime.datetime.now()

    backup_periods = BackupPeriod.objects.filter(start_date__lte=now, end_date__gte=now)
    backup_accounts = Backup.objects.filter(member=member, period__in=backup_periods, approved=True)

    status_badges = ['info', 'success', 'warning', 'danger']

    context = {
        'member': member,
        'backup_accounts': backup_accounts,
        'status_badges': status_badges,
        'accounts': accounts
    }

    return render(request, 'client_area/accounts.html', context)


@login_required
def accounts_team(request):
    member = Member.objects.get(user=request.user)
    teams = member.team

    accounts = {}
    for team in teams.all():
        accounts[team.id] = Client.objects.filter(team=team).filter(Q(status=1) | Q(status=0))

    status_badges = ['info', 'success', 'warning', 'danger']

    context = {
        'member': member,
        'status_badges': status_badges,
        'teams': teams,
        'accounts': accounts
    }

    return render(request, 'client_area/accounts_team.html', context)


@login_required
def accounts_all(request):
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    accounts = Client.objects.filter(Q(status=1) | Q(status=0))

    status_badges = ['info', 'success', 'warning', 'danger']

    context = {
        'status_badges': status_badges,
        'accounts': accounts
    }

    return render(request, 'client_area/accounts_all.html', context)


@login_required
def account_new(request):
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    if request.method == 'GET':
        teams = Team.objects.all()
        client_types = ClientType.objects.all()
        clients = ParentClient.objects.all()
        industries = Industry.objects.all()
        languages = Language.objects.all()
        members = Member.objects.all()
        services = Service.objects.all()
        fee_structures = ManagementFeesStructure.objects.all()
        tiers = [1, 2, 3]

        context = {
            'teams': teams,
            'client_types': client_types,
            'clients': clients,
            'industries': industries,
            'languages': languages,
            'members': members,
            'services': services,
            'tiers': tiers,
            'fee_structures': fee_structures
        }

        return render(request, 'client_area/account_new.html', context)
    elif request.method == 'POST':
        form_data = {
            'account_name': request.POST.get('account_name'),
            'team': request.POST.get('team'),
            'client_type': request.POST.get('client_type'),
            'industry': request.POST.get('industry'),
            'language': request.POST.get('language'),
            'tier': request.POST.get('tier'),
            'sold_by': request.POST.get('sold_by'),
            'status': request.POST.get('status'),
        }

        form = NewClientForm(form_data)

        if form.is_valid():
            cleaned_inputs = form.clean()

            # Make a contact object
            # contactInfo = ClientContact(name=cleaned_inputs['contact_name'], email=cleaned_inputs['contact_email'])

            # Get existing client
            if not int(request.POST.get('existing_client')) == 0:
                client = ParentClient.objects.get(id=request.POST.get('existing_client'))
            else:
                client = ParentClient.objects.create(name=request.POST.get('client_name'))

            account = Client.objects.create(client_name=cleaned_inputs['account_name'])
            # account.client_name = cleaned_inputs['account_name']
            account.industry = cleaned_inputs['industry']
            account.soldBy = cleaned_inputs['sold_by']
            account.clientType = cleaned_inputs['client_type']

            account.objective = request.POST.get('objective')
            account.sold_budget = request.POST.get('sold_budget')

            # contactInfo.save()
            # Handle contact info
            number_of_contacts = request.POST.get('contact_num_input')
            contact_array = []
            for i in range(1, int(number_of_contacts) + 1):
                contact = ClientContact()
                contact.name = request.POST.get('contact_name' + str(i))
                contact.email = request.POST.get('contact_email' + str(i))
                contact.phone = request.POST.get('contact_phone_number' + str(i))
                contact.save()
                contact_array.append(contact)

            account.contactInfo.set(contact_array)

            # set parent client
            account.parentClient = client

            # set teams
            # teams = [cleaned_inputs['team']]
            # account.team.set(teams)

            # set languages
            languages = [cleaned_inputs['language']]
            account.language.set(languages)

            # set PPC services
            # services = [cleaned_inputs['services']]
            # account.services.set(services)

            # set contact info
            # contacts = [contactInfo]

            # Make management fee structure
            fee_create_or_existing = request.POST.get('fee_structure_type')
            if fee_create_or_existing == '1':
                # Create new management fee
                number_of_tiers = request.POST.get('rowNumInput')
                fee_structure_name = request.POST.get('fee_structure_name')
                init_fee = request.POST.get('setup_fee')
                management_fee_structure = ManagementFeesStructure()
                management_fee_structure.name = fee_structure_name
                management_fee_structure.initialFee = init_fee
                management_fee_structure.save()
                for i in range(1, int(number_of_tiers) + 1):
                    fee_type = request.POST.get('fee-type' + str(i))
                    fee = request.POST.get('fee' + str(i))
                    lower_bound = request.POST.get('low-bound' + str(i))
                    high_bound = request.POST.get('high-bound' + str(i))
                    feeInterval = ManagementFeeInterval.objects.create(feeStyle=fee_type, fee=fee,
                                                                       lowerBound=lower_bound, upperBound=high_bound)
                    management_fee_structure.feeStructure.add(feeInterval)
                management_fee_structure.save()
                account.managementFee = management_fee_structure
            elif fee_create_or_existing == '2':
                # Use existing
                existing_fee_id = request.POST.get('existing_structure')
                management_fee_structure = get_object_or_404(ManagementFeesStructure, id=existing_fee_id)
                account.managementFee = management_fee_structure
            else:
                pass

            # Set up the sales profile (services) of the account
            # TODO: Eric, please fill this section out with corresponding front end components
            sp = SalesProfile.objects.create(account=account)

            # Check if we sold SEO and/or CRO
            # Repeat this process for every type of service (PPC doesn't have hours explicitly)
            if request.POST.get('seo_check'):
                # account.has_seo = True
                sp.seo_status = 1
                sp.save()
                account.seo_hours = request.POST.get('seo_hours')
            if request.POST.get('cro_check'):
                # account.has_cro = True
                sp.cro_status = 1
                sp.save()
                account.cro_hours = request.POST.get('cro_hours')

            account.has_gts = True
            account.has_budget = True
            account.has_ppc = True

            account.save()

            # Account is created, send out notifications to all necessary members
            staff_users = User.objects.filter(is_staff=True)
            staff_members = Member.objects.filter(user__in=staff_users)
            for staff_member in staff_members:
                Notification.objects.create(member=staff_member,
                                            message='New account won! Please assign members to new account ' + str(
                                                account),
                                            link='/clients/accounts/' + str(account.id),
                                            type=0,
                                            severity=2)

            # Create onboarding steps for this client
            if account.has_ppc:
                ppc_steps = OnboardingStep.objects.filter(service=0)
                for ppc_step in ppc_steps:
                    ppc_step_assignment = OnboardingStepAssignment.objects.create(step=ppc_step, account=account)
                    ppc_tasks = OnboardingTask.objects.filter(step=ppc_step)
                    for ppc_task in ppc_tasks:
                        OnboardingTaskAssignment.objects.create(step=ppc_step_assignment, task=ppc_task)
            if account.has_seo:
                seo_steps = OnboardingStep.objects.filter(service=1)
                for seo_step in seo_steps:
                    seo_step_assignment = OnboardingStepAssignment.objects.create(step=seo_step, account=account)
                    seo_tasks = OnboardingTask.objects.filter(step=seo_step)
                    for seo_task in seo_tasks:
                        OnboardingTaskAssignment.objects.create(step=seo_step_assignment, task=seo_task)
            if account.has_cro:
                cro_steps = OnboardingStep.objects.filter(service=2)
                for cro_step in cro_steps:
                    cro_step_assignment = OnboardingStepAssignment.objects.create(step=cro_step, account=account)
                    cro_tasks = OnboardingTask.objects.filter(step=cro_step)
                    for cro_task in cro_tasks:
                        OnboardingTaskAssignment.objects.create(step=cro_step_assignment, task=cro_task)

            event_description = account.client_name + ' was added to SparkView.'
            lc_event = LifecycleEvent.objects.create(account=account, type=1, description=event_description, phase=0,
                                                     phase_day=0, cycle=0,
                                                     bing_active=account.has_bing,
                                                     facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                     monthly_budget=account.current_budget, spend=account.current_spend)

            lc_event.members.set(account.assigned_members_array)
            lc_event.save()

            return redirect('/clients/accounts/all')
        else:
            return HttpResponse('Invalid form entries')
    else:
        return HttpResponse('You are at the wrong place')


@login_required
def account_edit_temp(request, id):
    """
    Temporary account edit page. Would not be surprised if this ends up being a permanent page as we add more stuff to it
    """
    member = Member.objects.get(user=request.user)
    if not request.user.is_staff and not member.has_account(id) and not member.teams_have_accounts(id):
        return HttpResponse('You do not have permission to view this page')

    if request.method == 'GET':
        account = Client.objects.get(id=id)
        management_fee_structures = ManagementFeesStructure.objects.all()
        inactive_reasons = account._meta.get_field('inactive_reason').choices
        lost_reasons = account._meta.get_field('lost_reason').choices

        context = {
            'account': account,
            'management_fee_structures': management_fee_structures,
            'inactive_reasons': inactive_reasons,
            'lost_reasons': lost_reasons
        }

        return render(request, 'client_area/account_edit_temp.html', context)
    elif request.method == 'POST':
        account = get_object_or_404(Client, id=id)

        account_name = request.POST.get('account_name')
        seo_hours = request.POST.get('seo_hours')
        cro_hours = request.POST.get('cro_hours')

        now = datetime.datetime.now()
        month = now.month
        year = now.year

        old_status = account.status

        status = request.POST.get('status')
        account.status = int(status)

        if old_status != 2 and account.status == 2:
            """
            Account is now inactive
            """
            inactive_reason = request.POST.get('account_inactive_reason')
            inactive_bc = request.POST.get('inactive_bc')
            inactive_return = request.POST.get('account_inactive_return')
            account.inactive_reason = inactive_reason

            if inactive_bc != '':
                account.inactive_bc_link = inactive_bc
            if inactive_return != '':
                account.inactive_return_date = datetime.datetime.strptime(inactive_return, '%Y-%m-%d')
            staff_users = User.objects.filter(is_staff=True)
            staff_members = Member.objects.filter(user__in=staff_users)
            for staff_member in staff_members:
                link = '/clients/accounts/' + str(account.id)
                message = str(account.client_name) + ' is now inactive (paused).'
                Notification.objects.create(member=staff_member, link=link, message=message, type=0, severity=3)

            event_description = account.client_name + ' was set to inactive. The reason is ' + str(
                inactive_reason) + '.'
            lc_event = LifecycleEvent.objects.create(account=account, type=3, description=event_description,
                                                     phase=account.phase,
                                                     phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                     bing_active=account.has_bing,
                                                     facebook_active=account.has_fb,
                                                     adwords_active=account.has_adwords,
                                                     monthly_budget=account.current_budget,
                                                     spend=account.current_spend)

            lc_event.members.set(account.assigned_members_array)
            lc_event.save()

        if old_status != 3 and account.status == 3:
            """
            Account is now lost
            """
            lost_reason = request.POST.get('account_lost_reason')
            account.lost_reason = lost_reason
            lost_bc = request.POST.get('lost_bc')
            if lost_bc != '':
                account.lost_bc_link = lost_bc
            staff_users = User.objects.filter(is_staff=True)
            staff_members = Member.objects.filter(user__in=staff_users)
            for staff_member in staff_members:
                link = '/clients/accounts/' + str(account.id)
                message = str(account.client_name) + ' has been lost.'
                Notification.objects.create(member=staff_member, link=link, message=message, type=0, severity=3)

            event_description = account.client_name + ' was set to lost. The reason is ' + str(
                lost_reason) + '.'
            lc_event = LifecycleEvent.objects.create(account=account, type=5, description=event_description,
                                                     phase=account.phase,
                                                     phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                     bing_active=account.has_bing,
                                                     facebook_active=account.has_fb,
                                                     adwords_active=account.has_adwords,
                                                     monthly_budget=account.current_budget,
                                                     spend=account.current_spend)

            lc_event.members.set(account.assigned_members_array)
            lc_event.save()

        fee_override = request.POST.get('fee_override')
        hours_override = request.POST.get('hours_override')

        if account.client_name != account_name:
            # Audit log There
            account.client_name = account_name

        if seo_hours != '' and float(seo_hours) != 0.0:
            account.has_seo = True
            account.seo_hours = seo_hours
        else:
            account.has_seo = False
            account.seo_hours = 0.0

        if cro_hours != '' and float(cro_hours) != 0.0:
            account.has_cro = True
            account.cro_hours = cro_hours
        else:
            account.has_cro = False
            account.cro_hours = 0.0

        if request.user.is_staff:
            if fee_override != 'None':
                account.management_fee_override = float(fee_override)
            if hours_override != 'None':
                account.allocated_ppc_override = float(hours_override)
            if 'advanced_reporting' in request.POST:
                account.advanced_reporting = True
            else:
                account.advanced_reporting = False

        # Make management fee structure
        if request.user.is_staff and 'mf_check' in request.POST:
            fee_create_or_existing = request.POST.get('fee_structure_type')
            if fee_create_or_existing == '1':
                # Create new management fee
                number_of_tiers = request.POST.get('rowNumInput')
                fee_structure_name = request.POST.get('fee_structure_name')
                init_fee = request.POST.get('setup_fee')
                management_fee_structure = ManagementFeesStructure()
                management_fee_structure.name = fee_structure_name
                management_fee_structure.initialFee = init_fee
                management_fee_structure.save()
                for i in range(1, int(number_of_tiers) + 1):
                    fee_type = request.POST.get('fee-type' + str(i))
                    fee = request.POST.get('fee' + str(i))
                    lower_bound = request.POST.get('low-bound' + str(i))
                    high_bound = request.POST.get('high-bound' + str(i))
                    fee_interval = ManagementFeeInterval.objects.create(feeStyle=fee_type, fee=fee,
                                                                        lowerBound=lower_bound, upperBound=high_bound)
                    management_fee_structure.feeStructure.add(fee_interval)
                management_fee_structure.save()
                account.managementFee = management_fee_structure
            elif fee_create_or_existing == '2':
                # Use existing
                existing_fee_id = request.POST.get('existing_structure')
                management_fee_structure = get_object_or_404(ManagementFeesStructure, id=existing_fee_id)
                account.managementFee = management_fee_structure
            else:
                pass

        account.save()

        return redirect('/clients/accounts/' + str(account.id))


@login_required
def account_edit(request, id):
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    if request.method == 'GET':
        account = Client.objects.get(id=id)
        teams = Team.objects.all()
        client_types = ClientType.objects.all()
        industries = Industry.objects.all()
        languages = Language.objects.all()
        members = Member.objects.all()
        services = Service.objects.all()
        statuses = Client._meta.get_field('status').choices
        tiers = [1, 2, 3]

        context = {
            'account': account,
            'teams': teams,
            'client_types': client_types,
            'industries': industries,
            'languages': languages,
            'members': members,
            'statuses': statuses,
            'services': services,
            'tiers': tiers
        }

        return render(request, 'client_area/account_edit.html', context)
    elif request.method == 'POST':
        account = get_object_or_404(Client, id=id)

        member = Member.objects.get(user=request.user)

        form_data = {
            'account_name': request.POST.get('account_name'),
            'team': request.POST.get('team'),
            'client_type': request.POST.get('client_type'),
            'industry': request.POST.get('industry'),
            'language': request.POST.get('language'),
            'contact_email': request.POST.get('contact_email'),
            'contact_name': request.POST.get('contact_name'),
            'sold_by': request.POST.get('soldby'),
            'services': request.POST.get('services'),
            'status': request.POST.get('status'),
        }

        form = NewClientForm(form_data)

        if form.is_valid():
            cleaned_inputs = form.clean()

            # Make a contact object
            contactInfo = ClientContact(name=cleaned_inputs['contact_name'], email=cleaned_inputs['contact_email'])

            # Bad boilerplate
            # Change this eventually
            if account.client_name != cleaned_inputs['account_name']:
                AccountChanges.objects.create(account=account, member=member, changeField='account_name',
                                              changedFrom=account.client_name, changedTo=cleaned_inputs['account_name'])
                account.client_name = cleaned_inputs['account_name']

            if account.clientType != cleaned_inputs['client_type']:
                AccountChanges.objects.create(account=account, member=member, changeField='client_type',
                                              changedFrom=account.clientType.name,
                                              changedTo=cleaned_inputs['client_type'])
                account.clientType = cleaned_inputs['client_type']

            if account.industry != cleaned_inputs['industry']:
                AccountChanges.objects.create(account=account, member=member, changeField='industry',
                                              changedFrom=account.industry.name, changedTo=cleaned_inputs['industry'])
                account.industry = cleaned_inputs['industry']

            if account.soldBy != cleaned_inputs['sold_by']:
                AccountChanges.objects.create(account=account, member=member, changeField='sold_by',
                                              changedFrom=account.soldBy.user.first_name + ' ' + account.soldBy.user.last_name,
                                              changedTo=cleaned_inputs['sold_by'])
                account.soldBy = cleaned_inputs['sold_by']

            if account.status != cleaned_inputs['status']:
                AccountChanges.objects.create(account=account, member=member, changeField='status',
                                              changedFrom=account.status, changedTo=cleaned_inputs['status'])
                account.status = cleaned_inputs['status']

            contactInfo.save()

            # set teams
            teams = [cleaned_inputs['team']]
            account.team.set(teams)

            # set languages
            languages = [cleaned_inputs['language']]
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
    # member = Member.objects.get(user=request.user)
    """
    The following flag needs to be turned off for now
    """
    # if not request.user.is_staff and not member.has_account(id) and not member.teams_have_accounts(id):
    #     return HttpResponse('You do not have permission to view this page')
    account = Client.objects.get(id=id)
    members = Member.objects.all()
    changes = AccountChanges.objects.filter(account=account)

    # Get hours this month for this account
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    accountHoursThisMonth = AccountHourRecord.objects.filter(account=account, month=month, year=year, is_unpaid=False)

    accountsHoursThisMonthByMember = AccountHourRecord.objects.filter(account=account, month=month, year=year,
                                                                      is_unpaid=False).values('member', 'month',
                                                                                              'year').annotate(
        Sum('hours'))
    accountsValueHoursThisMonthByMember = AccountHourRecord.objects.filter(account=account, month=month, year=year,
                                                                           is_unpaid=True).values('member', 'month',
                                                                                                  'year').annotate(
        Sum('hours'))

    backup_periods = BackupPeriod.objects.filter(start_date__lte=now, end_date__gte=now)
    backups = Backup.objects.filter(account=account, period__in=backup_periods, approved=True)

    for row in accountsHoursThisMonthByMember:
        try:
            row['member'] = members.get(id=row['member'])
        except Member.DoesNotExist:
            pass

    for row in accountsValueHoursThisMonthByMember:
        try:
            row['member'] = members.get(id=row['member'])
        except Member.DoesNotExist:
            pass

    seven_days_ago = now - datetime.timedelta(7)

    promos = Promo.objects.filter(account=account, end_date__gte=seven_days_ago)

    status_badges = ['info', 'success', 'warning', 'danger']

    context = {
        'account': account,
        'members': members,
        'backups': backups,
        'accountHoursMember': accountsHoursThisMonthByMember,
        'value_hours_member': accountsValueHoursThisMonthByMember,
        'changes': changes,
        'accountHoursThisMonth': accountHoursThisMonth,
        'status_badges': status_badges,
        'kpid': account.kpi_info,
        'promos': promos
    }

    return render(request, 'client_area/account_single.html', context)


@login_required
def account_assign_members(request):
    account_id = request.POST.get('account_id')
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page. Only admins can assign members now.')

    account = Client.objects.get(id=account_id)

    # There may be a better way to handle this form
    # This is terrible boilerplate
    # CMS
    cm1_id = request.POST.get('cm1-assign')
    if cm1_id == '0':
        member = None
    else:
        member = Member.objects.get(id=cm1_id)
    account.cm1 = member

    cm2_id = request.POST.get('cm2-assign')
    if cm2_id == '0':
        member = None
    else:
        member = Member.objects.get(id=cm2_id)
    account.cm2 = member

    cm3_id = request.POST.get('cm3-assign')
    if cm3_id == '0':
        member = None
    else:
        member = Member.objects.get(id=cm3_id)
    account.cm3 = member

    # AMs
    am1_id = request.POST.get('am1-assign')
    if am1_id == '0':
        member = None
    else:
        member = Member.objects.get(id=am1_id)
    account.am1 = member

    am2_id = request.POST.get('am2-assign')
    if am2_id == '0':
        member = None
    else:
        member = Member.objects.get(id=am2_id)
    account.am2 = member

    am3_id = request.POST.get('am3-assign')
    if am3_id == '0':
        member = None
    else:
        member = Member.objects.get(id=am3_id)
    account.am3 = member

    # SEO
    seo1_id = request.POST.get('seo1-assign')
    if seo1_id == '0':
        member = None
    else:
        member = Member.objects.get(id=seo1_id)
    account.seo1 = member

    seo2_id = request.POST.get('seo2-assign')
    if seo2_id == '0':
        member = None
    else:
        member = Member.objects.get(id=seo2_id)
    account.seo2 = member

    seo3_id = request.POST.get('seo3-assign')
    if seo3_id == '0':
        member = None
    else:
        member = Member.objects.get(id=seo3_id)
    account.seo3 = member

    # Strat
    srtat1_id = request.POST.get('strat1-assign')
    if srtat1_id == '0':
        member = None
    else:
        member = Member.objects.get(id=srtat1_id)
    account.strat1 = member

    srtat2_id = request.POST.get('strat2-assign')
    if srtat2_id == '0':
        member = None
    else:
        member = Member.objects.get(id=srtat2_id)
    account.strat2 = member

    srtat3_id = request.POST.get('strat3-assign')
    if srtat3_id == '0':
        member = None
    else:
        member = Member.objects.get(id=srtat3_id)
    account.strat3 = member

    account.save()

    event_description = account.client_name + ' members changed.'
    lc_event = LifecycleEvent.objects.create(account=account, type=11, description=event_description,
                                             phase=account.phase,
                                             phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                             bing_active=account.has_bing,
                                             facebook_active=account.has_fb,
                                             adwords_active=account.has_adwords,
                                             monthly_budget=account.current_budget,
                                             spend=account.current_spend)

    lc_event.members.set(account.assigned_members_array)
    lc_event.save()

    return redirect('/clients/accounts/' + str(account.id))


@login_required
def add_hours_to_account(request):
    if request.method == 'GET':
        member = Member.objects.get(user=request.user)
        accounts = Client.objects.filter(
            Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
            Q(am1=member) | Q(am2=member) | Q(am3=member) |
            Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
            Q(strat1=member) | Q(strat2=member) | Q(strat3=member)
        ).order_by('client_name')

        all_accounts = Client.objects.all().order_by('client_name')

        months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
        years = [2018, 2019, 2020, 2021, 2022, 2023]

        now = datetime.datetime.now()
        monthnow = now.month
        current_year = now.year

        members = Member.objects.none
        if request.user.is_staff:
            # Reason for this is that this members list if used for the training hours, which is staff only
            members = Member.objects.all()

        context = {
            'member': member,
            'all_accounts': all_accounts,
            'accounts': accounts,
            'months': months,
            'monthnow': monthnow,
            'years': years,
            'members': members,
            'current_year': current_year
        }

        return render(request, 'client_area/insert_hours.html', context)

    elif request.method == 'POST':
        member = Member.objects.get(user=request.user)
        accounts = Client.objects.filter(
            Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
            Q(am1=member) | Q(am2=member) | Q(am3=member) |
            Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
            Q(strat1=member) | Q(strat2=member) | Q(strat3=member)
        ).order_by('client_name')
        accounts_count = accounts.count()

        for i in range(accounts_count):
            i = str(i)
            account_id = request.POST.get('account-id-' + i)
            account = Client.objects.get(id=account_id)

            if not request.user.is_staff and not member.has_account(account_id):
                return HttpResponse('You do not have permission to add hours to this account')
            member = Member.objects.get(user=request.user)
            hours = request.POST.get('hours-' + i)
            try:
                hours = float(hours)
            except (TypeError, ValueError):
                continue
            month = request.POST.get('month-' + i)
            year = request.POST.get('year-' + i)

            AccountHourRecord.objects.create(member=member, account=account, hours=hours, month=month, year=year)

        return redirect('/clients/accounts/report_hours')


@login_required
def value_added_hours(request):
    if request.method == 'GET':
        return HttpResponse('You should not be here')
    elif request.method == 'POST':
        account_id = request.POST.get('account_id')
        account = Client.objects.get(id=account_id)
        # if (not request.user.is_staff and not member.has_account(account_id)):
        #     return HttpResponse('You do not have permission to add hours to this account')
        member = Member.objects.get(user=request.user)
        hours = request.POST.get('hours')
        month = request.POST.get('month')
        year = request.POST.get('year')

        AccountHourRecord.objects.create(member=member, account=account, hours=hours, month=month, year=year,
                                         is_unpaid=True)

        return redirect('/clients/accounts/report_hours')


@login_required
def account_allocate_percentages(request):
    member = Member.objects.get(user=request.user)
    account_id = request.POST.get('account_id')
    account = Client.objects.get(id=account_id)
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    # There may be a better way to handle this form
    # This is boilerplate
    # CMs
    cm1percent = request.POST.get('cm1-percent')
    if cm1percent is None or cm1percent == '':
        cm1percent = 0
    account.cm1percent = cm1percent

    cm2percent = request.POST.get('cm2-percent')
    if cm2percent is None or cm2percent == '':
        cm2percent = 0
    account.cm2percent = cm2percent

    cm3percent = request.POST.get('cm3-percent')
    if cm3percent is None or cm3percent == '':
        cm3percent = 0
    account.cm3percent = cm3percent

    am1percent = request.POST.get('am1-percent')
    if am1percent is None or am1percent == '':
        am1percent = 0
    account.am1percent = am1percent

    am2percent = request.POST.get('am2-percent')
    if am2percent is None or am2percent == '':
        am2percent = 0
    account.am2percent = am2percent

    am3percent = request.POST.get('am3-percent')
    if am3percent is None or am3percent == '':
        am3percent = 0
    account.am3percent = am3percent

    seo1percent = request.POST.get('seo1-percent')
    if seo1percent is None or seo1percent == '':
        seo1percent = 0
    account.seo1percent = seo1percent

    seo2percent = request.POST.get('seo2-percent')
    if seo2percent is None or seo2percent == '':
        seo2percent = 0
    account.seo2percent = seo2percent

    seo3percent = request.POST.get('seo3-percent')
    if seo3percent is None or seo3percent == '':
        seo3percent = 0
    account.seo3percent = seo3percent

    strat1percent = request.POST.get('strat1-percent')
    if strat1percent is None or strat1percent == '':
        strat1percent = 0
    account.strat1percent = strat1percent

    strat2percent = request.POST.get('strat2-percent')
    if strat2percent is None or strat2percent == '':
        strat2percent = 0
    account.strat2percent = strat2percent

    strat3percent = request.POST.get('strat3-percent')
    if strat3percent is None or strat3percent == '':
        strat3percent = 0
    account.strat3percent = strat3percent

    account.save()

    return redirect('/clients/accounts/' + str(account.id))


@login_required
def get_management_fee_details(request, id):
    """
    Returns a json format of a management fee structure. Used to render them dynamically
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    fee_structure = get_object_or_404(ManagementFeesStructure, id=id)

    fsj = {
        'initial_fee': fee_structure.initialFee,
        'fee_intervals': {}
    }

    count = 0
    for fee_interval in fee_structure.feeStructure.all():
        fsj['fee_intervals'][count] = {}
        fsj['fee_intervals'][count]['style'] = fee_interval.feeStyle
        fsj['fee_intervals'][count]['lowerBound'] = fee_interval.lowerBound
        fsj['fee_intervals'][count]['upperBound'] = fee_interval.upperBound
        fsj['fee_intervals'][count]['fee'] = fee_interval.fee
        count += 1

    return JsonResponse(fsj)


@login_required
def confirm_sent_am(request):
    """
    Sets a report's 'sent to am' date
    """
    if request.method == 'GET':
        return HttpResponse('Invalid request')
    member = Member.objects.get(user=request.user)
    account_id = request.POST.get('account_id')
    account = Client.objects.get(id=account_id)
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    report = MonthlyReport.objects.get(account=account, month=request.POST.get('month'))

    report.date_sent_to_am = timezone.now()
    report.save()

    resp = {
        'response': report.date_sent_to_am
    }

    return JsonResponse(resp)


@login_required
def confirm_sent_client(request):
    """
    Sets a report's 'sent to client' date
    """
    if request.method == 'GET':
        return HttpResponse('Invalid request')
    member = Member.objects.get(user=request.user)
    account_id = request.POST.get('account_id')
    account = Client.objects.get(id=account_id)
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    report = MonthlyReport.objects.get(account=account, month=request.POST.get('month'))

    report.date_sent_by_am = timezone.now()
    report.save()

    resp = {
        'response': report.date_sent_by_am
    }

    return JsonResponse(resp)


@login_required
def set_due_date(request):
    """
    Sets a report's due date
    """
    if request.method == 'GET':
        return HttpResponse('Invalid request')
    member = Member.objects.get(user=request.user)
    account_id = request.POST.get('account_id')
    account = Client.objects.get(id=account_id)
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    report = MonthlyReport.objects.get(account=account, month=request.POST.get('month'))

    report.due_date = datetime.datetime.strptime(request.POST.get('due_date'), "%Y-%m-%d")
    report.save()

    resp = {
        'response': report.due_date
    }

    return JsonResponse(resp)


@login_required
def new_promo(request):
    """
    Creates a new promo
    """
    if request.method == 'GET':
        return HttpResponse('Invalid request')
    account_id = request.POST.get('account_id')
    account = Client.objects.get(id=account_id)
    member = Member.objects.get(user=request.user)
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    promo_name = request.POST.get('promo-name')
    promo_start_date = request.POST.get('start-date')
    promo_end_date = request.POST.get('end-date')
    promo_desc = request.POST.get('promo-desc')

    promo_has_aw = request.POST.get('has-aw')
    promo_has_fb = request.POST.get('has-fb')
    promo_has_bing = request.POST.get('has-bing')
    promo_has_other = request.POST.get('has-other')

    promo = Promo()
    promo.name = promo_name
    promo.account = account
    promo.start_date = datetime.datetime.strptime(promo_start_date, "%Y-%m-%d %H:%M")
    promo.end_date = datetime.datetime.strptime(promo_end_date, "%Y-%m-%d %H:%M")
    promo.desc = promo_desc
    if promo_has_aw:
        promo.has_aw = True
    if promo_has_fb:
        promo.has_fb = True
    if promo_has_bing:
        promo.has_bing = True
    if promo_has_other:
        promo.has_other = True
    promo.is_indefinite = False  # change eventually
    promo.save()

    return redirect('/clients/accounts/' + str(account_id))


@login_required
def confirm_promo(request):
    """
    Confirms the beginning or end of a promo (done by CM or AM)
    """
    if request.method == 'GET':
        return HttpResponse('Invalid request')
    account_id = request.POST.get('account_id')
    member = Member.objects.get(user=request.user)
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    promo = get_object_or_404(Promo, id=int(request.POST.get('promo_id')))

    type_of_confirmation = int(request.POST.get('confirmation_type'))

    if type_of_confirmation == 0:  # This means we are confirming the promo started
        promo.confirmed_started = datetime.datetime.now()
    elif type_of_confirmation == 1:  # This means we are confirming the promo ended
        promo.confirmed_ended = datetime.datetime.now()

    promo.save()

    return HttpResponse('Success! Promo confirmed')


@login_required
def star_account(request):
    """
    Stars or unstars an account
    """
    if request.method == 'GET':
        return HttpResponse('Invalid request')
    account_id = request.POST.get('account_id')
    member = Member.objects.get(user=request.user)
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    bc_link = request.POST.get('bc_link')
    if bc_link is None or bc_link == '':
        return HttpResponse('You need to enter a basecamp link to flag an account')

    account = Client.objects.get(id=account_id)
    # set_to_star = str(request.POST.get('star_flag')) == '0' # If its 0, then we need to set star to true, else false

    now = datetime.datetime.now()
    account.flagged_bc_link = bc_link
    account.flagged_datetime = now
    account.star_flag = True
    account.save()

    event_description = account.client_name + ' was flagged by ' + member.user.get_full_name() + '.'
    notes = 'Basecamp link: ' + account.flagged_bc_link
    lc_event = LifecycleEvent.objects.create(account=account, type=8, description=event_description,
                                             phase=account.phase,
                                             phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                             bing_active=account.has_bing,
                                             facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                             monthly_budget=account.current_budget, spend=account.current_spend,
                                             notes=notes)

    lc_event.members.set(account.assigned_members_array)
    lc_event.save()

    return redirect('/clients/accounts/' + str(account.id))


@login_required
def assign_member_flagged_account(request):
    """
    Assigns a member to a flagged account
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    member = Member.objects.get(id=request.POST.get('member'))
    flagged_account = Client.objects.get(id=request.POST.get('account'))

    flagged_account.flagged_assigned_member = member
    flagged_account.save()

    event_description = member.user.get_full_name() + ' was assigned to deal with the flagged account.'
    lc_event = LifecycleEvent.objects.create(account=flagged_account, type=10, description=event_description,
                                             phase=flagged_account.phase,
                                             phase_day=flagged_account.phase_day,
                                             cycle=flagged_account.ninety_day_cycle,
                                             bing_active=flagged_account.has_bing,
                                             facebook_active=flagged_account.has_fb,
                                             adwords_active=flagged_account.has_adwords,
                                             monthly_budget=flagged_account.current_budget,
                                             spend=flagged_account.current_spend)

    lc_event.members.set(flagged_account.assigned_members_array)
    lc_event.save()

    return redirect('/reports/flagged_accounts')


@login_required
def edit_promos(request):
    """
    Page that lets you edit promos
    """
    member = Member.objects.get(user=request.user)
    now = datetime.datetime.now()
    accounts = member.accounts.filter(Q(status=0) | Q(status=1))
    backup_periods = BackupPeriod.objects.filter(start_date__lte=now, end_date__gte=now)
    backups = Backup.objects.filter(member=member, period__in=backup_periods, approved=True)
    backup_accounts = []

    for backup in backups:
        backup_accounts.append(backup.account)

    promos = Promo.objects.filter(Q(account__in=accounts) | Q(account__in=backup_accounts))

    if request.method == 'POST':
        promo_id = request.POST.get('promo_id')
        member = Member.objects.get(user=request.user)
        if not request.user.is_staff and not promos.filter(id=promo_id).exists():
            return HttpResponse('You do not have permission to view this page')

        promo_name = request.POST.get('promo-name')
        promo_start_date = request.POST.get('start-date')
        promo_end_date = request.POST.get('end-date')

        promo = Promo.objects.get(id=promo_id)
        promo.name = promo_name
        promo.start_date = datetime.datetime.strptime(promo_start_date, "%Y-%m-%d %H:%M")
        promo.end_date = datetime.datetime.strptime(promo_end_date, "%Y-%m-%d %H:%M")
        promo.save()

    context = {
        'promos': promos
    }

    return render(request, 'client_area/edit_promos.html', context)


@login_required
def set_kpis(request):
    """
    Sets the KPIs for an account
    """
    member = Member.objects.get(user=request.user)
    account_id = int(request.POST.get('account_id'))
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    account = Client.objects.get(id=account_id)
    roas = request.POST.get('set-roas')
    cpa = request.POST.get('set-cpa')

    if roas is not None and roas != '' and float(roas) != 0:
        account.target_roas = roas

    if cpa is not None and cpa != '' and float(cpa) != 0:
        account.target_cpa = cpa

    account.save()

    return redirect('/clients/accounts/' + str(account.id))


@login_required
def set_services(request):
    """
    Sets the services for an account
    """
    member = Member.objects.get(user=request.user)
    account_id = int(request.POST.get('account_id'))
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    account = Client.objects.get(id=account_id)
    sales_profile = SalesProfile.objects.get(account=account)

    # update service statuses
    try:
        ppc = int(request.POST.get('set-ppc'))
    except ValueError:
        ppc = 6  # set to None by default
    try:
        seo = int(request.POST.get('set-seo'))
    except ValueError:
        seo = 6
    try:
        cro = int(request.POST.get('set-cro'))
    except ValueError:
        cro = 6
    try:
        strat = int(request.POST.get('set-strat'))
    except ValueError:
        strat = 6
    try:
        email_marketing = int(request.POST.get('set-email-marketing'))
    except ValueError:
        email_marketing = 6
    try:
        feed_management = int(request.POST.get('set-feed-management'))
    except ValueError:
        feed_management = 6

    status_range = range(0, len(sales_profile.STATUS_CHOICES))
    if ppc is not None and ppc in status_range:
        sales_profile.ppc_status = ppc
    if seo is not None and seo in status_range:
        sales_profile.seo_status = seo
    if cro is not None and cro in status_range:
        sales_profile.cro_status = cro
    if strat is not None and strat in status_range:
        sales_profile.strat_status = strat
    if email_marketing is not None and email_marketing in status_range:
        sales_profile.email_status = email_marketing
    if feed_management is not None and feed_management in status_range:
        sales_profile.feed_status = feed_management

    sales_profile.save()

    return redirect('/clients/accounts/' + str(account.id))


@login_required
def onboard_account(request, account_id):
    """
    Client onboarding page
    :param request:
    :param account_id:
    :return:
    """
    member = Member.objects.get(user=request.user)
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponse('You do not have permission to view this page')

    account = Client.objects.get(id=account_id)

    if request.method == 'GET':
        s_ac_ppc_steps = None
        s_ac_seo_steps = None
        s_ac_cro_steps = None
        s_ac_strat_steps = None

        if account.has_ppc:
            ppc_step = OnboardingStep.objects.filter(service=0)
            ac_ppc_steps = OnboardingStepAssignment.objects.filter(step__in=ppc_step, account=account)
            s_ac_ppc_steps = sorted(ac_ppc_steps, key=lambda t: t.step.order)
        if account.has_seo:
            seo_step = OnboardingStep.objects.filter(service=1)
            ac_seo_steps = OnboardingStepAssignment.objects.filter(step__in=seo_step, account=account)
            s_ac_seo_steps = sorted(ac_seo_steps, key=lambda t: t.step.order)
        if account.has_cro:
            cro_step = OnboardingStep.objects.filter(service=2)
            ac_cro_steps = OnboardingStepAssignment.objects.filter(step__in=cro_step, account=account)
            s_ac_cro_steps = sorted(ac_cro_steps, key=lambda t: t.step.order)
        if account.has_strat:
            strat_step = OnboardingStep.objects.filter(service=3)
            ac_strat_steps = OnboardingStepAssignment.objects.filter(step__in=strat_step, account=account)
            s_ac_strat_steps = sorted(ac_strat_steps, key=lambda t: t.step.order)

        context = {
            'account': account,
            'ac_ppc_steps': s_ac_ppc_steps,
            'ac_seo_steps': s_ac_seo_steps,
            'ac_cro_steps': s_ac_cro_steps,
            'ac_strat_steps': s_ac_strat_steps,
        }

        return render(request, 'client_area/onboard_account.html', context)
    elif request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = OnboardingTaskAssignment.objects.get(id=task_id)
        account = task.step.account
        checked = request.POST.get('checked') == '1'
        if checked:
            task.complete = True
        else:
            task.complete = False
        task.save()

        step_complete = 0
        if task.step.complete:
            step_complete = 1

        acc_active = 1
        for step in account.onboardingstepassignment_set.all():
            if not step.complete:
                acc_active = 0
                break

        if acc_active == 1:
            account.status = 1
            account.save()

            event_description = account.client_name + ' completed onboarding.'
            lc_event = LifecycleEvent.objects.create(account=account, type=2, description=event_description,
                                                     phase=account.phase,
                                                     phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                     bing_active=account.has_bing,
                                                     facebook_active=account.has_fb,
                                                     adwords_active=account.has_adwords,
                                                     monthly_budget=account.current_budget,
                                                     spend=account.current_spend)

            lc_event.members.set(account.assigned_members_array)
            lc_event.save()

            event_description = account.client_name + ' became active.'
            lc_event2 = LifecycleEvent.objects.create(account=account, type=4, description=event_description,
                                                      phase=account.phase,
                                                      phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                      bing_active=account.has_bing,
                                                      facebook_active=account.has_fb,
                                                      adwords_active=account.has_adwords,
                                                      monthly_budget=account.current_budget,
                                                      spend=account.current_spend)

            lc_event2.members.set(account.assigned_members_array)
            lc_event2.save()

        resp = {
            'step_complete': step_complete,
            'step_id': task.step.id,
            'acc_active': acc_active
        }

        return JsonResponse(resp)
    else:
        return HttpResponse('Invalid request type')


@login_required
def account_lifecycle(request, account_id):
    """
    View for account lifecycle (90 days of awesome)
    :param request:
    :param account_id:
    :return:
    """
    account = Client.objects.get(id=account_id)
    events = LifecycleEvent.objects.filter(account=account).order_by('-date_created')

    last_inactive = events.filter(type=3).order_by('-date_created')
    last_inactive_date = None
    last_inactive_reason = None
    if last_inactive.count() > 0:
        last_inactive_date = last_inactive[0].date_created
        last_inactive_reason = last_inactive[0].notes

    last_lost = events.filter(type=5).order_by('-date_created')
    last_lost_date = None
    last_lost_reason = None
    if last_lost.count() > 0:
        last_lost_date = last_lost[0].date_created
        last_lost_reason = last_lost[0].notes

    times_flagged = events.filter(type=8).count()
    transition_number = events.filter(type=11).count()

    context = {
        'account': account,
        'events': events,
        'last_inactive_date': last_inactive_date,
        'last_inactive_reason': last_inactive_reason,
        'last_lost_date': last_lost_date,
        'last_lost_reason': last_lost_reason,
        'times_flagged': times_flagged,
        'transition_number': transition_number,
    }

    return render(request, 'client_area/account_lifecycle.html', context)


@login_required
def campaigns(request, account_id):
    """
    Shows campaigns of an account
    :param request:
    :param account_id:
    :return:
    """
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return HttpResponse('Invalid client')

    context = {
        'account': account
    }

    return render(request, 'client_area/campaigns.html', context)
