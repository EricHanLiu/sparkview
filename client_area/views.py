from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
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
    OnboardingStep, OnboardingTaskAssignment, OnboardingTask, LifecycleEvent, SalesProfile, OpportunityDescription, \
    PitchedDescription, MandateType, Mandate, MandateAssignment, MandateHourRecord, Opportunity, Pitch, Tag
from insights.models import TenInsightsReport
from .forms import NewClientForm
from budget.cron import create_default_budget
from bloom.utils.utils import get_last_month, member_locked_out
from tasks.logger import Logger
import json
from django.core.serializers import serialize


@login_required
def accounts(request):
    member = Member.objects.get(user=request.user)
    accounts = member.accounts_not_lost

    now = datetime.datetime.now()

    backup_periods = BackupPeriod.objects.filter(start_date__lte=now, end_date__gte=now)
    backup_accounts = Backup.objects.filter(members__in=[member], period__in=backup_periods, approved=True)

    status_badges = ['info', 'success', 'warning', 'danger']

    context = {
        'member': member,
        'backup_accounts': backup_accounts,
        'status_badges': status_badges,
        'accounts': accounts
    }

    return render(request, 'client_area/refactor/accounts.html', context)


@login_required
def accounts_team(request):
    member = Member.objects.get(user=request.user)
    teams = member.team

    accounts = {}
    for team in teams.all():
        accounts[team.id] = Client.objects.filter(team=team).filter(Q(status=1) | Q(status=0)).order_by('client_name')

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
        return HttpResponseForbidden('You do not have permission to view this page')

    accounts = Client.objects.filter(Q(status=1) | Q(status=0)).order_by('client_name')

    status_badges = ['info', 'success', 'warning', 'danger']

    context = {
        'page_type': 'Active',
        'status_badges': status_badges,
        'accounts': accounts,
    }

    return render(request, 'client_area/refactor/accounts_all.html', context)


@login_required
def accounts_inactive(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    accounts = Client.objects.filter(status=2).order_by('client_name')

    status_badges = ['info', 'success', 'warning', 'danger']

    context = {
        'page_type': 'Inactive',
        'status_badges': status_badges,
        'accounts': accounts,
    }

    return render(request, 'client_area/refactor/accounts_all.html', context)


@login_required
def accounts_lost(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    accounts = Client.objects.filter(status=3).order_by('client_name')

    status_badges = ['info', 'success', 'warning', 'danger']

    context = {
        'page_type': 'Lost',
        'status_badges': status_badges,
        'accounts': accounts,
    }

    return render(request, 'client_area/refactor/accounts_all.html', context)


@login_required
def account_new(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'GET':
        teams = Team.objects.all()
        client_types = ClientType.objects.all()
        clients = ParentClient.objects.all().order_by('name')
        industries = Industry.objects.all()
        languages = Language.objects.all()
        members = Member.objects.filter(deactivated=False).order_by('user__first_name')
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

        return render(request, 'client_area/refactor/account_new.html', context)
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
                try:
                    init_fee = float(request.POST.get('setup_fee'))
                except ValueError:
                    init_fee = 0.0
                management_fee_structure = ManagementFeesStructure()
                management_fee_structure.name = fee_structure_name
                management_fee_structure.initialFee = init_fee
                management_fee_structure.save()
                for i in range(1, int(number_of_tiers) + 1):
                    fee_type = request.POST.get('fee-type' + str(i))
                    try:
                        fee = float(request.POST.get('fee' + str(i)))
                    except ValueError:
                        fee = 0.0
                    try:
                        lower_bound = float(request.POST.get('low-bound' + str(i)))
                    except ValueError:
                        lower_bound = 0.0
                    try:
                        high_bound = float(request.POST.get('high-bound' + str(i)))
                    except ValueError:
                        high_bound = 0.0
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
            sp = SalesProfile.objects.create(account=account)

            # Check if we sold each service
            if request.POST.get('seo_check'):
                # account.has_seo = True
                sp.seo_status = 0
                sp.save()
                account.seo_hours = request.POST.get('seo_hours')
            if request.POST.get('cro_check'):
                # account.has_cro = True
                sp.cro_status = 0
                sp.save()
                account.cro_hours = request.POST.get('cro_hours')
            if request.POST.get('ppc_check'):
                sp.ppc_status = 0
                sp.save()

            account.has_gts = True
            account.has_budget = True

            account.save()

            # Account is created, send out notifications to all necessary members
            staff_users = User.objects.filter(is_staff=True)
            staff_members = Member.objects.filter(user__in=staff_users, deactivated=False)
            for staff_member in staff_members:
                Notification.objects.create(member=staff_member,
                                            message='New account won! Please assign members to new account ' + str(
                                                account),
                                            link='/clients/accounts/' + str(account.id),
                                            type=0,
                                            severity=2)

            # Create onboarding steps for this client
            # if account.is_onboarding_ppc:
            #     ppc_steps = OnboardingStep.objects.filter(service=0)
            #     for ppc_step in ppc_steps:
            #         ppc_step_assignment = OnboardingStepAssignment.objects.create(step=ppc_step, account=account)
            #         ppc_tasks = OnboardingTask.objects.filter(step=ppc_step)
            #         for ppc_task in ppc_tasks:
            #             OnboardingTaskAssignment.objects.create(step=ppc_step_assignment, task=ppc_task)
            # if account.is_onboarding_seo:
            #     seo_steps = OnboardingStep.objects.filter(service=1)
            #     for seo_step in seo_steps:
            #         seo_step_assignment = OnboardingStepAssignment.objects.create(step=seo_step, account=account)
            #         seo_tasks = OnboardingTask.objects.filter(step=seo_step)
            #         for seo_task in seo_tasks:
            #             OnboardingTaskAssignment.objects.create(step=seo_step_assignment, task=seo_task)
            # if account.is_onboarding_cro:
            #     cro_steps = OnboardingStep.objects.filter(service=2)
            #     for cro_step in cro_steps:
            #         cro_step_assignment = OnboardingStepAssignment.objects.create(step=cro_step, account=account)
            #         cro_tasks = OnboardingTask.objects.filter(step=cro_step)
            #         for cro_task in cro_tasks:
            #             OnboardingTaskAssignment.objects.create(step=cro_step_assignment, task=cro_task)

            # Create new onboarding steps
            steps = OnboardingStep.objects.all()
            for step in steps:
                OnboardingStepAssignment.objects.create(account=account, step=step)

            event_description = account.client_name + ' was added to SparkView.'
            lc_event = LifecycleEvent.objects.create(account=account, type=1, description=event_description, phase=0,
                                                     phase_day=0, cycle=0,
                                                     bing_active=account.has_bing,
                                                     facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                     monthly_budget=account.current_budget, spend=account.current_spend)

            lc_event.members.set(account.assigned_members_array)
            lc_event.save()

            # set onboarding hours bank
            now = datetime.datetime.now()
            account.onboarding_hours_allocated_this_month_field = account.onboarding_hours_remaining_total()
            account.onboarding_hours_allocated_updated_timestamp = now
            account.save()

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
        return HttpResponseForbidden('You do not have permission to view this page')

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
            if inactive_return != '0':
                account.inactive_reason = inactive_reason

            if inactive_bc != '':
                account.inactive_bc_link = inactive_bc
            if inactive_return != '':
                account.inactive_return_date = datetime.datetime.strptime(inactive_return, '%Y-%m-%d')
            staff_users = User.objects.filter(is_staff=True)
            staff_members = Member.objects.filter(user__in=staff_users, deactivated=False)
            account.save()
            message = str(account.client_name) + ' is now inactive (paused).'
            for staff_member in staff_members:
                link = '/clients/accounts/' + str(account.id)
                Notification.objects.create(member=staff_member, link=link, message=message, type=0, severity=3)

            logger = Logger()
            in_reason_id, in_reason_display = Client.INACTIVE_CHOICES[int(account.inactive_reason)]
            short_desc = account.client_name + ' is now inactive for the following reason: ' + in_reason_display
            logger.send_account_lost_email(short_desc, message)

            sp = account.sales_profile

            if sp.ppc_status == 1:
                sp.ppc_status = 2
            if sp.seo_status == 1:
                sp.seo_status = 2
            if sp.cro_status == 1:
                sp.cro_status = 2
            sp.save()

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
            if lost_reason != '0':
                account.lost_reason = lost_reason
            lost_bc = request.POST.get('lost_bc')
            if lost_bc != '':
                account.lost_bc_link = lost_bc
            staff_users = User.objects.filter(is_staff=True)
            staff_members = Member.objects.filter(user__in=staff_users, deactivated=False)
            message = str(account.client_name) + ' has been lost.'
            account.save()
            for staff_member in staff_members:
                link = '/clients/accounts/' + str(account.id)
                Notification.objects.create(member=staff_member, link=link, message=message, type=0, severity=3)

            logger = Logger()
            print(account.get_lost_reason_display())
            lost_reason_id, lost_reason_display = Client.LOST_CHOICES[int(account.lost_reason)]
            short_desc = account.client_name + ' is now lost for the following reason: ' + lost_reason_display
            logger.send_account_lost_email(short_desc, message)

            sp = account.sales_profile

            if sp.ppc_status == 1:
                sp.ppc_status = 2
            if sp.seo_status == 1:
                sp.seo_status = 2
            if sp.cro_status == 1:
                sp.cro_status = 2
            sp.save()

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

        sp, created = SalesProfile.objects.get_or_create(account=account)

        if seo_hours != '' and float(seo_hours) != 0.0:
            sp.seo_status = 1
            account.seo_hours = seo_hours
        else:
            if sp.seo_status != 2:
                sp.seo_status = 6
                account.seo_hours = 0.0

        if cro_hours != '' and float(cro_hours) != 0.0:
            sp.cro_status = 1
            account.cro_hours = cro_hours
        else:
            if sp.cro_status != 2:
                sp.cro_status = 6
                account.cro_hours = 0.0

        sp.save()

        if request.user.is_staff:
            if fee_override != 'None':
                account.management_fee_override = float(fee_override)
            if hours_override != 'None':
                account.allocated_ppc_override = float(hours_override)
            else:
                account.allocated_ppc_override = None
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
def account_edit(request, account_id):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'GET':
        account = Client.objects.get(id=account_id)
        teams = Team.objects.all()
        client_types = ClientType.objects.all()
        industries = Industry.objects.all()
        languages = Language.objects.all()
        members = Member.objects.filter(deactivated=False).order_by('user__first_name')
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
def account_single(request, account_id):
    # member = Member.objects.get(user=request.user)
    """
    The following flag needs to be turned off for now
    """
    # if not request.user.is_staff and not member.has_account(id) and not member.teams_have_accounts(id):
    #     return HttpResponseForbidden('You do not have permission to view this page')
    if request.method == 'GET':
        if request.user.member.is_locked_out:
            return redirect('/user_management/members/' + str(request.user.member.id) + '/input_hours')

        account = Client.objects.get(id=account_id)
        members = Member.objects.filter(deactivated=False).order_by('user__first_name')
        changes = AccountChanges.objects.filter(account=account)

        # Get hours this month for this account
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        accountHoursThisMonth = AccountHourRecord.objects.filter(account=account, month=month, year=year,
                                                                 is_unpaid=False)

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

        opps = OpportunityDescription.objects.all()
        pitches = PitchedDescription.objects.all()

        mandate_types = MandateType.objects.all()
        try:
            first_mandate_rate = mandate_types[0].hourly_rate
        except IndexError:
            first_mandate_rate = ''

        months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
        now = datetime.datetime.now()
        years = [i for i in range(2018, now.year + 2)]

        mandate_hours_this_month = MandateHourRecord.objects.filter(assignment__mandate__account=account, month=month,
                                                                    year=year)

        # Pretty bad for speed of the page... we'll see how badly it affects it
        additional_services = MandateType.objects.all()
        opp_reasons = OpportunityDescription.objects.all()

        management_fee_structures = ManagementFeesStructure.objects.all()

        inactive_reasons = Client.INACTIVE_CHOICES
        lost_reasons = Client.LOST_CHOICES
        account_status_classes = ['is-info', 'is-success', 'is-warning', 'is-danger']
        account_status_class = account_status_classes[account.status]

        budgets = sorted(account.budgets, key=lambda b: b.projected_spend_avg - b.budget)

        context = {
            'account': account,
            'members': members,
            'backups': backups,
            'inactive_reasons': inactive_reasons,
            'lost_reasons': lost_reasons,
            'management_fee_structures': management_fee_structures,
            'accountHoursMember': accountsHoursThisMonthByMember,
            'value_hours_member': accountsValueHoursThisMonthByMember,
            'changes': changes,
            'accountHoursThisMonth': accountHoursThisMonth,
            'status_badges': status_badges,
            'kpid': account.kpi_info,
            'promos': promos,
            'opps': opps,
            'pitches': pitches,
            'mandate_types': mandate_types,
            'first_mandate_rate': first_mandate_rate,
            'mandate_hours_this_month': mandate_hours_this_month,
            'months': months,
            'monthnow': str(now.month),
            'years': years,
            'current_year': now.year,
            'additional_services': additional_services,
            'opp_reasons': opp_reasons,
            'title': str(account) + ' - SparkView',
            'account_status_class': account_status_class,
            'budgets': budgets
        }

        return render(request, 'client_area/refactor/client_profile.html', context)
    elif request.method == 'POST':
        account = Client.objects.get(id=account_id)
        member = Member.objects.get(user=request.user)

        hours = request.POST.get('quick_add_hours')
        month = request.POST.get('quick_add_month')
        year = request.POST.get('quick_add_year')

        if not member.has_account(account_id):
            return HttpResponseForbidden()

        try:
            hours = float(hours)
        except (TypeError, ValueError):
            hours = 0

        is_onboarding = account.status == 0
        if hours > 0:
            AccountHourRecord.objects.create(member=member, account=account, hours=hours, month=month, year=year,
                                             is_onboarding=is_onboarding)

        return HttpResponse()


@login_required
def account_single_old(request, account_id):
    # member = Member.objects.get(user=request.user)
    """
    The following flag needs to be turned off for now
    """
    # if not request.user.is_staff and not member.has_account(id) and not member.teams_have_accounts(id):
    #     return HttpResponseForbidden('You do not have permission to view this page')
    if request.method == 'GET':
        account = Client.objects.get(id=account_id)
        members = Member.objects.filter(deactivated=False).order_by('user__first_name')
        changes = AccountChanges.objects.filter(account=account)

        # Get hours this month for this account
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        accountHoursThisMonth = AccountHourRecord.objects.filter(account=account, month=month, year=year,
                                                                 is_unpaid=False)

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

        opps = OpportunityDescription.objects.all()
        pitches = PitchedDescription.objects.all()

        mandate_types = MandateType.objects.all()
        try:
            first_mandate_rate = mandate_types[0].hourly_rate
        except IndexError:
            first_mandate_rate = ''

        months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
        now = datetime.datetime.now()
        years = [i for i in range(2018, now.year + 1)]

        mandate_hours_this_month = MandateHourRecord.objects.filter(assignment__mandate__account=account, month=month,
                                                                    year=year)

        # Pretty bad for speed of the page... we'll see how badly it affects it
        additional_services = MandateType.objects.all()
        opp_reasons = OpportunityDescription.objects.all()

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
            'promos': promos,
            'opps': opps,
            'pitches': pitches,
            'mandate_types': mandate_types,
            'first_mandate_rate': first_mandate_rate,
            'mandate_hours_this_month': mandate_hours_this_month,
            'months': months,
            'monthnow': now.month,
            'years': years,
            'current_year': now.year,
            'additional_services': additional_services,
            'opp_reasons': opp_reasons,
            'title': str(account) + ' - SparkView'
        }

        return render(request, 'client_area/account_single.html', context)
    elif request.method == 'POST':
        account = Client.objects.get(id=account_id)
        member = Member.objects.get(user=request.user)

        hours = request.POST.get('quick_add_hours')
        month = request.POST.get('quick_add_month')
        year = request.POST.get('quick_add_year')

        if not member.has_account(account_id):
            return HttpResponseForbidden()

        try:
            hours = float(hours)
        except (TypeError, ValueError):
            hours = 0

        is_onboarding = account.status == 0
        if hours > 0:
            AccountHourRecord.objects.create(member=member, account=account, hours=hours, month=month, year=year,
                                             is_onboarding=is_onboarding)

        return HttpResponse()


@login_required
def account_assign_members(request):
    account_id = request.POST.get('account_id')
    request_member = request.user.member
    if not request.user.is_staff and not request_member.has_account(
            account_id) and not request_member.teams_have_accounts(account_id):
        return HttpResponseForbidden('You do not have permission to view this page.')

    account = Client.objects.get(id=account_id)

    # There may be a better way to handle this form
    # This is terrible boilerplate
    # CMS
    cm1_id = request.POST.get('cm1_assign')
    if cm1_id == '0' or cm1_id is None:
        member = None
    else:
        member = Member.objects.get(id=cm1_id)
    cm1_percent = request.POST.get('cm1_percent')
    if cm1_percent is None or cm1_percent == '':
        cm1_percent = 0
    account.cm1percent = cm1_percent
    if request.user.is_staff:
        account.cm1 = member

    cm2_id = request.POST.get('cm2_assign')
    if cm2_id == '0' or cm2_id is None:
        member = None
    else:
        member = Member.objects.get(id=cm2_id)
    cm2_percent = request.POST.get('cm2_percent')
    if cm2_percent is None or cm2_percent == '':
        cm2_percent = 0
    account.cm2percent = cm2_percent
    if request.user.is_staff:
        account.cm2 = member

    cm3_id = request.POST.get('cm3_assign')
    if cm3_id == '0' or cm3_id is None:
        member = None
    else:
        member = Member.objects.get(id=cm3_id)
    cm3_percent = request.POST.get('cm3_percent')
    if cm3_percent is None or cm3_percent == '':
        cm3_percent = 0
    account.cm3percent = cm3_percent
    if request.user.is_staff:
        account.cm3 = member

    # AMs
    am1_id = request.POST.get('am1_assign')
    if am1_id == '0' or am1_id is None:
        member = None
    else:
        member = Member.objects.get(id=am1_id)
    am1_percent = request.POST.get('am1_percent')
    if am1_percent is None or am1_percent == '':
        am1_percent = 0
    account.am1percent = am1_percent
    if request.user.is_staff:
        account.am1 = member

    am2_id = request.POST.get('am2_assign')
    if am2_id == '0' or am2_id is None:
        member = None
    else:
        member = Member.objects.get(id=am2_id)
    am2_percent = request.POST.get('am2_percent')
    if am2_percent is None or am2_percent == '':
        am2_percent = 0
    account.am2percent = am2_percent
    if request.user.is_staff:
        account.am2 = member

    am3_id = request.POST.get('am3_assign')
    if am3_id == '0' or am3_id is None:
        member = None
    else:
        member = Member.objects.get(id=am3_id)
    am3_percent = request.POST.get('am3_percent')
    if am3_percent is None or am3_percent == '':
        am3_percent = 0
    account.am3percent = am3_percent
    if request.user.is_staff:
        account.am3 = member

    # SEO
    seo1_id = request.POST.get('seo1_assign')
    if seo1_id == '0' or seo1_id is None:
        member = None
    else:
        member = Member.objects.get(id=seo1_id)
    seo1_percent = request.POST.get('seo1_percent')
    if seo1_percent is None or seo1_percent == '':
        seo1_percent = 0
    account.seo1percent = seo1_percent
    if request.user.is_staff:
        account.seo1 = member

    seo2_id = request.POST.get('seo2_assign')
    if seo2_id == '0' or seo2_id is None:
        member = None
    else:
        member = Member.objects.get(id=seo2_id)
    seo2_percent = request.POST.get('seo2_percent')
    if seo2_percent is None or seo2_percent == '':
        seo2_percent = 0
    account.seo2percent = seo2_percent
    if request.user.is_staff:
        account.seo2 = member

    seo3_id = request.POST.get('seo3_assign')
    if seo3_id == '0' or seo3_id is None:
        member = None
    else:
        member = Member.objects.get(id=seo3_id)
    seo3_percent = request.POST.get('seo3_percent')
    if seo3_percent is None or seo3_percent == '':
        seo3_percent = 0
    account.seo3percent = seo3_percent
    if request.user.is_staff:
        account.seo3 = member

    # Strat
    strat1_id = request.POST.get('strat1_assign')
    if strat1_id == '0' or strat1_id is None:
        member = None
    else:
        member = Member.objects.get(id=strat1_id)
    strat1_percent = request.POST.get('strat1_percent')
    if strat1_percent is None or strat1_percent == '':
        strat1_percent = 0
    account.strat1percent = strat1_percent
    if request.user.is_staff:
        account.strat1 = member

    strat2_id = request.POST.get('strat2_assign')
    if strat2_id == '0' or strat2_id is None:
        member = None
    else:
        member = Member.objects.get(id=strat2_id)
    strat2_percent = request.POST.get('strat2_percent')
    if strat2_percent is None or strat2_percent == '':
        strat2_percent = 0
    account.strat2percent = strat2_percent
    if request.user.is_staff:
        account.strat2 = member

    strat3_id = request.POST.get('strat3_assign')
    if strat3_id == '0' or strat3_id is None:
        member = None
    else:
        member = Member.objects.get(id=strat3_id)
    strat3_percent = request.POST.get('strat3_percent')
    if strat3_percent is None or strat3_percent == '':
        strat3_percent = 0
    account.strat3percent = strat3_percent
    if request.user.is_staff:
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
        ).filter(Q(status=0) | Q(status=1)).order_by('client_name')

        all_accounts = Client.objects.all().order_by('client_name')

        months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
        now = datetime.datetime.now()
        years = [i for i in range(2018, now.year + 1)]

        monthnow = now.month
        current_year = now.year

        members = Member.objects.none
        if request.user.is_staff:
            # Reason for this is that this members list if used for the training hours, which is staff only
            members = Member.objects.filter(deactivated=False).order_by('user__first_name')

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
        ).filter(Q(status=0) | Q(status=1)).order_by('client_name')
        accounts_count = accounts.count()
        for i in range(accounts_count):
            i = str(i)
            account_id = request.POST.get('account-id-' + i)
            account = Client.objects.get(id=account_id)

            if not request.user.is_staff and not member.has_account(account_id):
                return HttpResponseForbidden('You do not have permission to add hours to this account')
            member = Member.objects.get(user=request.user)
            hours = request.POST.get('hours-' + i)
            try:
                hours = float(hours)
            except (TypeError, ValueError):
                continue
            month = request.POST.get('month-' + i)
            year = request.POST.get('year-' + i)

            if hours > 0:
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
        #     return HttpResponseForbidden('You do not have permission to add hours to this account')
        member = Member.objects.get(user=request.user)
        hours = float(request.POST.get('hours'))
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))

        is_onboarding = account.status == 0
        if hours > 0:
            AccountHourRecord.objects.create(member=member, account=account, hours=hours, month=month, year=year,
                                             is_unpaid=True, is_onboarding=is_onboarding)

        # return redirect('/clients/accounts/report_hours')
        # keep everything on profile page
        return redirect('/user_management/members/' + str(member.id) + '/input_hours')


@login_required
def get_management_fee_details(request, id):
    """
    Returns a json format of a management fee structure. Used to render them dynamically
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

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
        return HttpResponseForbidden('You do not have permission to view this page')

    report = MonthlyReport.objects.get(account=account, month=request.POST.get('month'), year=request.POST.get('year'))

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
        return HttpResponseForbidden('You do not have permission to view this page')

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
        return HttpResponseForbidden('You do not have permission to view this page')

    report = MonthlyReport.objects.get(account=account, month=request.POST.get('month'), year=request.POST.get('year'))

    report.due_date = datetime.datetime.strptime(request.POST.get('due_date'), "%m/%d/%Y")
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
        return HttpResponseForbidden('You do not have permission to view this page')

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
    try:
        promo.start_date = datetime.datetime.strptime(promo_start_date, "%Y-%m-%d %H:%M")
        promo.end_date = datetime.datetime.strptime(promo_end_date, "%Y-%m-%d %H:%M")
    except ValueError:  # to handle new (refactored) client profile datepicker and old one simultaneously
        promo.start_date = datetime.datetime.strptime(promo_start_date, "%m/%d/%Y %H:%M")
        promo.end_date = datetime.datetime.strptime(promo_end_date, "%m/%d/%Y %H:%M")
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
        return HttpResponseForbidden('You do not have permission to view this page')

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
        return HttpResponseForbidden('You do not have permission to view this page')

    flagged = request.POST.get('flagged') == 'True'
    bc_link = request.POST.get('bc_link')
    if (bc_link is None or bc_link == '') and flagged:
        return HttpResponse('You need to enter a basecamp link to flag an account')

    account = Client.objects.get(id=account_id)

    if not flagged:
        account.star_flag = False
        account.flagged_bc_link = bc_link
        account.save()

        event_description = account.client_name + ' was marked as good by ' + member.user.get_full_name() + '.'
        notes = bc_link if bc_link != '' else ''
        lc_event = LifecycleEvent.objects.create(account=account, type=13, description=event_description,
                                                 phase=account.phase,
                                                 phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                 bing_active=account.has_bing,
                                                 facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                 monthly_budget=account.current_budget, spend=account.current_spend,
                                                 notes=notes)
        lc_event.members.set(account.assigned_members_array)
        lc_event.save()

        return redirect('/clients/accounts/' + str(account.id))

    now = datetime.datetime.now()
    account.flagged_bc_link = bc_link
    account.flagged_datetime = now
    account.star_flag = True
    account.num_times_flagged = account.num_times_flagged + 1
    account.save()

    event_description = account.client_name + ' was flagged by ' + member.user.get_full_name() + '.'
    notes = account.flagged_bc_link
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
        return HttpResponseForbidden('You do not have permission to view this page')

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
    if request.user.is_staff:
        promos = Promo.objects.all()
    else:
        promos = Promo.objects.filter(Q(account__in=accounts) | Q(account__in=member.backup_accounts))

    if request.method == 'POST':
        promo_id = request.POST.get('promo_id')
        member = Member.objects.get(user=request.user)
        if not request.user.is_staff and not promos.filter(id=promo_id).exists():
            return HttpResponseForbidden('You do not have permission to view this page')

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
        return HttpResponseForbidden('You do not have permission to view this page')

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
        return HttpResponseForbidden('You do not have permission to view this page')

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

    if ppc is not None:
        sales_profile.ppc_status = ppc
    if seo is not None:
        sales_profile.seo_status = seo
    if cro is not None:
        sales_profile.cro_status = cro

    sales_profile.save()

    if sales_profile.ppc_status == 1 and account.default_budget is None:
        create_default_budget(account_id)

    return redirect('/clients/accounts/' + str(account.id))


@login_required
def complete_onboarding_step(request):
    """
    Mark an onboarding step as completed for an account
    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request type')

    member = Member.objects.get(user=request.user)
    account_id = request.POST.get('account_id')
    if not request.user.is_staff and not member.has_account(account_id):
        return HttpResponseForbidden('You do not have permission to view this page')

    account = get_object_or_404(Client, id=account_id)

    now = datetime.datetime.now()
    assignment_id = request.POST.get('assignment_id')
    assignment = get_object_or_404(OnboardingStepAssignment, id=assignment_id)
    assignment.complete = True
    assignment.completed = now
    assignment.save()

    account_active = True
    for step in account.onboardingstepassignment_set.all():
        if not step.complete:
            account_active = False
            break

    if account_active:
        sp, created = SalesProfile.objects.get_or_create(account=account)
        sp.ppc_status = 1
        sp.save()

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

    return HttpResponse()


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
        return HttpResponseForbidden('You do not have permission to view this page')

    account = Client.objects.get(id=account_id)

    if request.method == 'GET':
        steps = OnboardingStepAssignment.objects.filter(account=account)

        context = {
            'account': account,
            'steps': steps
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
            for step in account.onboardingstepassignment_set.all():
                sp = account.sales_profile
                if step.step.service == 0:
                    sp.ppc_status = 1
                    sp.save()
                elif step.step.service == 1:
                    sp.seo_status = 1
                    sp.save()
                elif step.step.service == 2:
                    sp.cro_status = 1
                    sp.save()

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


def create_mandate(request):
    """
    View to create mandate
    :param request:
    :return:
    """
    account_id = request.POST.get('account_id')
    member = Member.objects.get(user=request.user)
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponseForbidden('You do not have permission to do this')

    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return HttpResponse('Invalid client')

    try:
        mandate_type = MandateType.objects.get(id=request.POST.get('mandate_type'))
    except MandateType.DoesNotExist:
        return HttpResponse('Invalid mandate type')

    # Check if its an ongoing mandate or not
    if 'ongoing_check' in request.POST:
        hourly_rate = request.POST.get('monthly_hourly_rate')
        if 'hourly_check' in request.POST:
            hours = request.POST.get('monthly_hours')
            mandate = Mandate.objects.create(hourly_rate=hourly_rate, ongoing=True, ongoing_hours=hours,
                                             mandate_type=mandate_type, account=account, billing_style=0)
        else:
            cost = request.POST.get('monthly_cost')
            mandate = Mandate.objects.create(hourly_rate=hourly_rate, ongoing=True, ongoing_cost=cost,
                                             mandate_type=mandate_type, account=account, billing_style=1)
    else:
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        cost = request.POST.get('cost')
        hourly_rate = request.POST.get('hourly_rate')

        try:
            start_date_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            start_date_dt = datetime.datetime.strptime(start_date, '%m/%d/%Y')
            end_date_dt = datetime.datetime.strptime(end_date, '%m/%d/%Y')

        mandate = Mandate.objects.create(cost=cost, hourly_rate=hourly_rate, start_date=start_date_dt,
                                         end_date=end_date_dt,
                                         account=account, mandate_type=mandate_type)

    mandate_members = request.POST.getlist('mandate_member')
    mandate_percentages = request.POST.getlist('percentage')

    for i in range(len(mandate_members)):
        MandateAssignment.objects.create(mandate=mandate, member_id=mandate_members[i],
                                         percentage=mandate_percentages[i])

    return redirect('/clients/accounts/' + str(account.id))


def set_opportunity(request):
    """
    Sets opportunity
    :param request:
    :return:
    """
    account_id = request.POST.get('account_id')
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return HttpResponseNotFound('That account does not exist')

    service_id = request.POST.get('service')
    reason_id = request.POST.get('opp_reason')
    try:
        opp_desc = OpportunityDescription.objects.get(id=reason_id)
    except OpportunityDescription.DoesNotExist:
        return HttpResponseNotFound('That opportunity description does not exist')

    if service_id == 'ppc':
        is_primary = True
        primary_service = 1
    elif service_id == 'seo':
        is_primary = True
        primary_service = 2
    elif service_id == 'cro':
        is_primary = True
        primary_service = 3
    else:
        is_primary = False
        try:
            additional_service = MandateType.objects.get(id=service_id)
        except MandateType.DoesNotExist:
            return HttpResponseNotFound('This service does not exist')

    if is_primary:
        # primary_service / additional_service will be defined, ignore warning
        opp, created = Opportunity.objects.get_or_create(account=account, primary_service=primary_service,
                                                         is_primary=True, addressed=False)
    else:
        opp, created = Opportunity.objects.get_or_create(account=account, additional_service=additional_service,
                                                         is_primary=False)

    opp.reason = opp_desc
    opp.flagged_by = request.user.member
    opp.save()

    return redirect('/clients/accounts/' + str(account.id))


def resolve_opportunity(request):
    """
    Resolves an opportunity
    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request type')

    opp_id = request.POST.get('opp_id')
    opp = get_object_or_404(Opportunity, id=opp_id)
    opp.addressed = True
    opp.save()

    return redirect('/reports/sales')


def update_opportunity(request):
    """
    Updates an opportunity's status
    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request type')

    opp_id = request.POST.get('opp_id')
    status = request.POST.get('status')

    opp = get_object_or_404(Opportunity, id=opp_id)
    opp.status = status
    if status == '2':
        opp.lost_reason = request.POST.get('lost_reason')
    opp.save()

    return redirect('/reports/sales')


def get_opportunities(request):
    """
    Returns all the unresolved (unaddressed) opportunities
    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request type')

    account = get_object_or_404(Client, id=request.POST.get('account_id'))
    opportunities = Opportunity.objects.filter(addressed=False, account=account)
    res = []
    for opp in opportunities:  # serializing only gives the IDs, need actual string representations
        res.append({'service': opp.service_string, 'created': opp.created})

    return JsonResponse({'opportunities': res}, safe=False)


def set_pitch(request):
    """
    Sets Pitch
    :param request:
    :return:
    """
    account_id = request.POST.get('account_id')
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return HttpResponseNotFound('That account does not exist')

    service_id = request.POST.get('service')
    reason_id = request.POST.get('opp_reason')
    try:
        opp_desc = OpportunityDescription.objects.get(id=reason_id)
    except OpportunityDescription.DoesNotExist:
        return HttpResponseNotFound('That opportunity description does not exist')

    pitch = Pitch()
    pitch.account = account
    pitch.reason = opp_desc

    if service_id == 'ppc':
        pitch.is_primary = True
        pitch.primary_service = 1
    elif service_id == 'seo':
        pitch.is_primary = True
        pitch.primary_service = 2
    elif service_id == 'cro':
        pitch.is_primary = True
        pitch.primary_service = 3
    else:
        pitch.is_primary = False
        try:
            service = MandateType.objects.get(id=service_id)
        except MandateType.DoesNotExist:
            return HttpResponseNotFound('This service does not exist')
        pitch.additional_service = service

    pitch.save()

    return redirect('/clients/accounts/' + str(account.id))


def edit_management_details(request):
    account_id = request.POST.get('account_id')
    member = Member.objects.get(user=request.user)
    if not request.user.is_staff and not member.has_account(account_id):
        return HttpResponseForbidden('You do not have permission to do this')

    account = get_object_or_404(Client, id=account_id)

    seo_hours = request.POST.get('seo_hours')
    cro_hours = request.POST.get('cro_hours')
    old_status = account.status
    account.status = int(request.POST.get('account_status'))

    if old_status != 2 and account.status == 2:
        """
        Account is now inactive
        """
        inactive_reason = request.POST.get('account_inactive_reason')
        inactive_bc = request.POST.get('inactive_bc')
        inactive_return = request.POST.get('account_inactive_return')
        if inactive_return != '0':
            account.inactive_reason = inactive_reason

        if inactive_bc != '':
            account.inactive_bc_link = inactive_bc
        if inactive_return != '':
            account.inactive_return_date = datetime.datetime.strptime(inactive_return, '%m/%d/%Y')
        staff_users = User.objects.filter(is_staff=True)
        staff_members = Member.objects.filter(user__in=staff_users, deactivated=False)
        account.save()
        message = str(account.client_name) + ' is now inactive (paused).'
        for staff_member in staff_members:
            link = '/clients/accounts/' + str(account.id)
            Notification.objects.create(member=staff_member, link=link, message=message, type=0, severity=3)

        logger = Logger()
        in_reason_id, in_reason_display = Client.INACTIVE_CHOICES[int(account.inactive_reason)]
        short_desc = account.client_name + ' is now inactive for the following reason: ' + in_reason_display
        logger.send_account_lost_email(short_desc, message)

        sp = account.sales_profile

        if sp.ppc_status == 1:
            sp.ppc_status = 2
        if sp.seo_status == 1:
            sp.seo_status = 2
        if sp.cro_status == 1:
            sp.cro_status = 2
        sp.save()

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
        if lost_reason != '0':
            account.lost_reason = lost_reason
        lost_bc = request.POST.get('lost_bc')
        if lost_bc != '':
            account.lost_bc_link = lost_bc
        staff_users = User.objects.filter(is_staff=True)
        staff_members = Member.objects.filter(user__in=staff_users, deactivated=False)
        message = str(account.client_name) + ' has been lost.'
        account.save()
        for staff_member in staff_members:
            link = '/clients/accounts/' + str(account.id)
            Notification.objects.create(member=staff_member, link=link, message=message, type=0, severity=3)

        logger = Logger()
        lost_reason_id, lost_reason_display = Client.LOST_CHOICES[int(account.lost_reason)]
        short_desc = account.client_name + ' is now lost for the following reason: ' + lost_reason_display
        logger.send_account_lost_email(short_desc, message)

        sp = account.sales_profile

        if sp.ppc_status == 1:
            sp.ppc_status = 2
        if sp.seo_status == 1:
            sp.seo_status = 2
        if sp.cro_status == 1:
            sp.cro_status = 2
        sp.save()

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

    if old_status != 0 and account.status == 0:
        """
        Account is now onboarding, create/reset steps
        """
        steps = OnboardingStep.objects.all()
        for step in steps:
            assignment, created = OnboardingStepAssignment.objects.get_or_create(account=account, step=step)
            assignment.complete = False
            assignment.save()

    fee_override = request.POST.get('fee_override')
    hours_override = request.POST.get('hours_override')

    if request.user.is_staff:
        if fee_override != 'None':
            account.management_fee_override = float(fee_override)
        if hours_override != 'None':
            account.allocated_ppc_override = float(hours_override)
        else:
            account.allocated_ppc_override = None

    sp, created = SalesProfile.objects.get_or_create(account=account)

    if seo_hours != '' and float(seo_hours) != 0.0:
        sp.seo_status = 1
        account.seo_hours = seo_hours
    else:
        if sp.seo_status != 2:
            sp.seo_status = 6
            account.seo_hours = 0.0

    if cro_hours != '' and float(cro_hours) != 0.0:
        sp.cro_status = 1
        account.cro_hours = cro_hours
    else:
        if sp.cro_status != 2:
            sp.cro_status = 6
            account.cro_hours = 0.0

    sp.save()

    # Make management fee structure
    fee_structure_name = request.POST.get('fee_structure_name')
    if request.user.is_staff and request.method == 'POST':
        fee_create_or_existing = request.POST.get('fee_structure_type')
        if fee_create_or_existing == '1' and fee_structure_name != '':
            # Create new management fee
            number_of_tiers = request.POST.get('row_num_input')
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
def get_client_details_objects(request):
    teams = Team.objects.all()
    industries = Industry.objects.all()
    tags = Tag.objects.all()

    data = {
        'teams': json.loads(serialize('json', teams)),
        'industries': json.loads(serialize('json', industries)),
        'tags': json.loads(serialize('json', tags))
    }
    return JsonResponse(data)


@login_required
def set_client_details(request):
    account_id = request.POST.get('account_id')
    member = request.user.member
    if not request.user.is_staff and not member.has_account(account_id):
        return HttpResponseForbidden('You do not have permission to do this')

    account_name = request.POST.get('account_name')
    bc_link = request.POST.get('bc_link')
    description = request.POST.get('description')
    notes = request.POST.get('notes')
    url = request.POST.get('url')
    contact_names = request.POST.getlist('contact_names')
    contact_emails = request.POST.getlist('contact_emails')
    contact_phones = request.POST.getlist('contact_phones')
    industry_id = request.POST.get('industry')
    team_ids = request.POST.getlist('teams')
    tags = request.POST.getlist('tags')

    account = Client.objects.get(id=account_id)
    account.client_name = account_name
    account.bc_link = bc_link
    account.description = description
    account.notes = notes
    account.url = url
    account.industry = Industry.objects.get(pk=industry_id)
    teams = Team.objects.filter(pk__in=team_ids)
    account.team.set(teams)
    account.tags.set(tags)

    for i, contact in enumerate(account.contactInfo.all()):
        contact.name = contact_names[i]
        contact.email = contact_emails[i]
        if contact_phones and contact_phones[i]:
            contact.phone = contact_phones[i]
        contact.save()

    account.save()

    return HttpResponse()


@login_required
def set_tags(request):
    """
    Sets tags for a client
    :param request: 
    :return: 
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request type')

    account_id = request.POST.get('account_id')
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return HttpResponseNotFound('That account does not exist')

    if not request.user.is_staff and not request.user.member.has_account(account_id):
        return HttpResponseForbidden('You do not have permission to set tags on this account')

    tag_ids = request.POST.getlist('tag_ids')
    new_tag_list = []
    for tag_id in tag_ids:
        try:
            tmp_tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            return HttpResponseBadRequest
        new_tag_list.append(tmp_tag)

    account.tags.clear()
    account.tags.set(new_tag_list)

    return HttpResponse('Successfully set tags')


@login_required
def ten_insights_report(request, account_id):
    """
    Gets account ten insights report
    :param request:
    :param account_id:
    :return:
    """
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return HttpResponseNotFound('That client does not exist')

    now = datetime.datetime.now()

    month = now.month
    year = now.year
    if 'month' in request.GET and 'year' in request.GET:
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))

    months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    years = [str(i) for i in range(2018, now.year + 1)]
    selected = {
        'month': str(month),
        'year': str(year)
    }

    # Temporary fix for now TODO: Fix this
    report_month, report_year = get_last_month(now)

    try:
        ten_insights_report_obj = TenInsightsReport.objects.get(account=account, month=report_month, year=report_year)
    except TenInsightsReport.DoesNotExist:
        return HttpResponseNotFound('Could not find any insights for the given time period!')

    # prepare for some jank
    reports = []
    for field in TenInsightsReport._meta.get_fields():
        field_name = str(field).split('.')[2]
        if field_name in ['id', 'account', 'ga_view', 'month', 'year', 'transaction_total_per_product_report',
                          'created']:
            continue
        report_json = json.loads(getattr(ten_insights_report_obj, field_name))
        header = report_json['reports'][0]['columnHeader']
        rows = report_json['reports'][0]['data']['rows']
        report = {
            'name': ' '.join(field_name.split('_')).title(),
            'dimension_header': header['dimensions'],
            'metric_header': header['metricHeader']['metricHeaderEntries'][0]['name'],
            'rows': [
                (row['dimensions'][0], row['metrics'][0]['values'][0]) for row in rows
            ]
        }
        reports.append(report)

    context = {
        'account': account,
        'months': months,
        'years': years,
        'selected': selected,
        'reports': reports
    }

    return render(request, 'client_area/refactor/ten_insights.html', context)
