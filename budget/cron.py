from bloom import celery_app, settings
from django.db.models import Q
from adwords_dashboard.models import Campaign, CampaignSpendDateRange
from facebook_dashboard.models import FacebookCampaign, FacebookCampaignSpendDateRange
from bing_dashboard.models import BingCampaign, BingCampaignSpendDateRange
from calendar import monthrange
from tasks.campaign_group_tasks import update_budget_campaigns
from bloom.utils.utils import perdelta, remove_accents, projected
from budget.models import Client, AccountBudgetSpendHistory, Budget
from adwords_dashboard.cron import get_spend_by_account_custom_daterange
from facebook_dashboard.cron import get_spend_by_facebook_account_custom_dates
from bing_dashboard.cron import get_spend_by_bing_account_custom_daterange
from client_area.models import PhaseTask, PhaseTaskAssignment
from notifications.models import Notification
from client_area.models import AccountAllocatedHoursHistory
from user_management.models import Member, MemberHourHistory
import datetime


@celery_app.task(bind=True)
def reset_all_campaign_spends(self):
    adwords_cmps = Campaign.objects.filter(
        Q(campaign_cost__gt=0) | Q(spend_until_yesterday__gt=0) | Q(campaign_yesterday_cost__gt=0))

    for cmp in adwords_cmps:
        if settings.DEBUG:
            reset_google_ads_campaign(cmp.id)
        else:
            reset_google_ads_campaign.delay(cmp.id)

    fb_cmps = FacebookCampaign.objects.filter(
        Q(campaign_cost__gt=0) | Q(spend_until_yesterday__gt=0) | Q(campaign_yesterday_cost__gt=0))

    for cmp in fb_cmps:
        if settings.DEBUG:
            reset_facebook_campaign(cmp.id)
        else:
            reset_facebook_campaign.delay(cmp.id)

    bing_cmps = BingCampaign.objects.filter(
        Q(campaign_cost__gt=0) | Q(spend_until_yesterday__gt=0) | Q(campaign_yesterday_cost__gt=0))

    for cmp in bing_cmps:
        if settings.DEBUG:
            reset_bing_campaign(cmp.id)
        else:
            reset_bing_campaign.delay(cmp.id)


@celery_app.task(bind=True)
def reset_google_ads_campaign(self, cmp_id):
    try:
        cmp = Campaign.objects.get(id=cmp_id)
    except Campaign.DoesNotExist:
        return

    print('Resetting adwords campaign: ' + str(cmp))
    cmp.campaign_yesterday_cost = 0
    cmp.spend_until_yesterday = 0
    cmp.campaign_cost = 0
    cmp.save()


@celery_app.task(bind=True)
def reset_facebook_campaign(self, cmp_id):
    try:
        cmp = FacebookCampaign.objects.get(id=cmp_id)
    except FacebookCampaign.DoesNotExist:
        return

    print('Resetting facebook campaign: ' + str(cmp))
    cmp.campaign_yesterday_cost = 0
    cmp.spend_until_yesterday = 0
    cmp.campaign_cost = 0
    cmp.save()


@celery_app.task(bind=True)
def reset_bing_campaign(self, cmp_id):
    try:
        cmp = BingCampaign.objects.get(id=cmp_id)
    except BingCampaign.DoesNotExist:
        return

    print('Resetting bing campaign: ' + str(cmp))
    cmp.campaign_yesterday_cost = 0
    cmp.spend_until_yesterday = 0
    cmp.campaign_cost = 0
    cmp.save()


@celery_app.task(bind=True)
def reset_all_flight_date_spend_objects(self):
    adwords_csdrs = CampaignSpendDateRange.objects.filter(Q(spend__gt=0) | Q(spend_until_yesterday__gt=0))

    for adwords_csdr in adwords_csdrs:
        if settings.DEBUG:
            reset_google_ads_campaign_spend_date_range(adwords_csdr.id)
        else:
            reset_google_ads_campaign_spend_date_range.delay(adwords_csdr.id)

    fb_csdrs = FacebookCampaignSpendDateRange.objects.filter(Q(spend__gt=0) | Q(spend_until_yesterday__gt=0))

    for fb_csdr in fb_csdrs:
        if settings.DEBUG:
            reset_facebook_campaign_spend_date_range(fb_csdr.id)
        else:
            reset_facebook_campaign_spend_date_range.delay(fb_csdr.id)

    bing_csdrs = BingCampaignSpendDateRange.objects.filter(Q(spend__gt=0) | Q(spend_until_yesterday__gt=0))

    for bing_csdr in bing_csdrs:
        if settings.DEBUG:
            reset_bing_campaign_spend_date_range(bing_csdr.id)
        else:
            reset_bing_campaign_spend_date_range.delay(bing_csdr.id)


@celery_app.task(bind=True)
def reset_google_ads_campaign_spend_date_range(self, csdr_id):
    """
    Resets a CampaignSpendDateRange object
    :param self:
    :param csdr_id:
    :return:
    """
    try:
        csdr = CampaignSpendDateRange.objects.get(id=csdr_id)
    except CampaignSpendDateRange.DoesNotExist:
        return

    print('Resetting adwords campaign daterange: ' + str(csdr))
    csdr.spend = 0
    csdr.spend_until_yesterday = 0
    csdr.save()


@celery_app.task(bind=True)
def reset_facebook_campaign_spend_date_range(self, csdr_id):
    """
    Resets a FacebookCampaignSpendDateRange object
    :param self:
    :param csdr_id:
    :return:
    """
    try:
        csdr = FacebookCampaignSpendDateRange.objects.get(id=csdr_id)
    except FacebookCampaignSpendDateRange.DoesNotExist:
        return

    print('Resetting fb campaign daterange: ' + str(csdr))
    csdr.spend = 0
    csdr.spend_until_yesterday = 0
    csdr.save()


@celery_app.task(bind=True)
def reset_bing_campaign_spend_date_range(self, csdr_id):
    """
    Resets a BingCampaignSpendDateRange object
    :param self:
    :param csdr_id:
    :return:
    """
    try:
        csdr = BingCampaignSpendDateRange.objects.get(id=csdr_id)
    except BingCampaignSpendDateRange.DoesNotExist:
        return

    print('Resetting bing campaign daterange: ' + str(csdr))
    csdr.spend = 0
    csdr.spend_until_yesterday = 0
    csdr.save()


@celery_app.task(bind=True)
def reset_all_budget_renewal_needs():
    """
    Resets all the budgets' need_renewing field. Should only be run on the first of the month
    """
    budgets = Budget.objects.filter(is_monthly=True)

    for budget in budgets:
        if settings.DEBUG:
            reset_google_ads_campaign(budget.id)
        else:
            reset_google_ads_campaign.delay(budget.id)


@celery_app.task(bind=True)
def reset_budget_renewal_needs(self, budget_id):
    try:
        budget = Budget.objects.get(id=budget_id)
    except Budget.DoesNotExist:
        return

    budget.needs_renewing = True
    budget.save()


@celery_app.task(bind=True)
def create_default_budgets(self):
    """
    Creates default budgets for accounts that don't have them yet
    :return:
    """
    default_budgets = Budget.objects.filter(is_default=True)
    account_ids_with_default_budgets = [budget.account.id for budget in default_budgets]

    accounts_without_default_budgets = Client.objects.filter(salesprofile__ppc_status=1).exclude(
        id__in=account_ids_with_default_budgets)

    for account in accounts_without_default_budgets:
        print('Making default budget for ' + str(account))
        create_default_budget(account.id)

    return 'create_default_budgets'


@celery_app.task(bind=True)
def create_default_budget(self, account_id):
    """
    Creates one default budget
    :param self:
    :param account_id:
    :return:
    """
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return

    budget = Budget.objects.create(name='Default Budget', account=account, is_monthly=True, grouping_type=2,
                                   is_default=True)
    if account.has_adwords:
        budget.has_adwords = True
    if account.has_fb:
        budget.has_facebook = True
    if account.has_bing:
        budget.has_bing = True

    budget.budget = account.current_budget
    budget.save()

    message = 'Created default budget for ' + str(account)
    print(message)

    return message


@celery_app.task(bind=True)
def update_default_budgets(self):
    """
    Updates default budgets to have correct ad networks
    :return:
    """
    default_budgets = Budget.objects.filter(is_default=True)

    for budget in default_budgets:
        account = budget.account
        if account.has_adwords:
            budget.has_adwords = True
        if account.has_fb:
            budget.has_facebook = True
        if account.has_bing:
            budget.has_bing = True
        budget.budget = account.current_budget
        budget.save()

        print('Budget ' + str(budget) + ' is now up to date')


@celery_app.task(bind=True)
def cron_clients(self):
    today = datetime.date.today() - datetime.relativedelta(days=1)
    first_day = datetime.date(today.year, today.month, 1)
    last_day = datetime.date(today.year, today.month, monthrange(today.year, today.month)[1])

    remaining = last_day.day - today.day
    pdays = []
    bdays = []

    for result in perdelta(today, last_day, datetime.timedelta(days=1)):
        pdays.append(result)

    for result in perdelta(first_day, last_day, datetime.timedelta(days=1)):
        bdays.append(result)

    clients = Client.objects.all()

    for client in clients:
        # S - Spend, P - Projected, B - Budget
        aw_s_final, aw_p_final, aw_b_final, gts_final = {}, {}, {}, {}
        bing_b_final, bing_p_final, bing_s_final = {}, {}, {}
        fb_b_final, fb_p_final, fb_s_final = {}, {}, {}

        aw_temp = 0.0
        fb_temp = 0.0

        client.budget = 0
        client.current_spend = 0
        client.aw_spend = 0
        client.bing_spend = 0
        client.fb_spend = 0
        client.aw_yesterday = 0
        client.bing_yesterday = 0
        client.fb_yesterday = 0
        client.aw_current_ds = 0
        client.bing_current_ds = 0
        client.fb_current_ds = 0
        client.aw_projected = 0
        client.bing_projected = 0
        client.fb_projected = 0
        client.aw_rec_ds = 0
        client.bing_rec_ds = 0
        client.fb_rec_ds = 0

        # Maybe this will work?
        client.budget += client.flex_budget

        client.save()

        adwords = client.adwords.all()
        if adwords:
            client.currency = client.adwords.all()[0].currency
        if len(adwords) > 0:

            for a in adwords:

                aw_budget, aw_spend, aw_projected, gts_values = {}, {}, {}, {}

                account_name = a.dependent_account_name
                client.budget += a.desired_spend
                client.current_spend += a.current_spend
                client.aw_spend += a.current_spend
                client.aw_yesterday += a.yesterday_spend
                client.aw_current_ds += a.current_spend / today.day
                for k, v in sorted(a.segmented_spend.items()):
                    try:
                        if v['cost'] == 0:
                            aw_temp = aw_temp + float(v['cost'])
                        else:
                            aw_temp = aw_temp + float(int(v['cost']) / 1000000)
                    except:
                        continue
                aw_s_final['A - ' + remove_accents(account_name) + ' Spend'] = aw_spend

                aw_projected_val = projected(a.current_spend, a.yesterday_spend)
                client.aw_projected += aw_projected_val
                if remaining > 0:
                    aw_projected_per_day = (aw_projected_val - a.current_spend) / remaining
                else:
                    aw_projected_per_day = (aw_projected_val - a.current_spend)
                for index, val in enumerate(pdays):
                    aw_projected[val.strftime('%Y-%m-%d')] = round((aw_projected_per_day * index) + a.current_spend, 2)
                aw_p_final['A - ' + remove_accents(a.dependent_account_name) + ' Projected'] = aw_projected

                # Budget only client
                if client.has_budget and not client.has_gts:
                    aw_budget_per_day = round(a.desired_spend / last_day.day, 2)
                    for index, val in enumerate(bdays, start=1):
                        aw_budget[val.strftime('%Y-%m-%d')] = round(aw_budget_per_day * index, 2)
                    aw_b_final['A - ' + remove_accents(a.dependent_account_name) + ' Budget'] = aw_budget

                    if remaining > 0:
                        client.aw_rec_ds += (a.desired_spend - a.current_spend) / remaining
                    else:
                        client.aw_rec_ds += a.desired_spend - a.current_spend

                # GTS only client
                elif client.has_gts and not client.has_budget:
                    gts_per_day = round(client.target_spend / last_day.day, 2)
                    for index, val in enumerate(bdays, start=1):
                        gts_values[val.strftime('%Y-%m-%d')] = round(gts_per_day * index, 2)
                    gts_final['Global Target Spend'] = gts_values

                    if remaining > 0:
                        client.aw_rec_ds += (client.target_spend - a.current_spend) / remaining
                    else:
                        client.aw_rec_ds += client.target_spend - a.current_spend

                # Both options active
                else:
                    gts_per_day = round(client.target_spend / last_day.day, 2)
                    for index, val in enumerate(bdays, start=1):
                        gts_values[val.strftime('%Y-%m-%d')] = round(gts_per_day * index, 2)
                    gts_final['Global Target Spend'] = gts_values

                    if a.desired_spend > 0:
                        aw_budget_per_day = round(a.desired_spend / last_day.day, 2)
                        for index, val in enumerate(bdays, start=1):
                            aw_budget[val.strftime('%Y-%m-%d')] = round(aw_budget_per_day * index, 2)
                        aw_b_final['A - ' + remove_accents(a.dependent_account_name) + ' Budget'] = aw_budget

                        if remaining > 0:
                            client.aw_rec_ds += (a.desired_spend - a.current_spend) / remaining
                        else:
                            client.aw_rec_ds += a.desired_spend - a.current_spend
                    else:
                        if remaining > 0:
                            client.aw_rec_ds += (a.desired_spend - a.current_spend) / remaining
                        else:
                            client.aw_rec_ds += a.desired_spend - a.current_spend

        else:
            gts_values = {}

            if client.has_gts and not client.has_budget:
                gts_per_day = round(client.target_spend / last_day.day, 2)
                for index, val in enumerate(bdays, start=1):
                    gts_values[val.strftime('%Y-%m-%d')] = round(gts_per_day * index, 2)
                gts_final['Global Target Spend'] = gts_values

        bing = client.bing.all()
        if len(bing) > 0:
            for b in bing:

                bing_budget, bing_spend, bing_projected = {}, {}, {}

                client.budget += b.desired_spend
                client.current_spend += b.current_spend
                client.bing_spend += b.current_spend
                client.bing_yesterday += b.yesterday_spend
                client.bing_current_ds += b.current_spend / today.day

                bing_s_final['B - ' + remove_accents(b.account_name) + ' Spend'] = bing_spend

                bing_projected_val = projected(b.current_spend, b.yesterday_spend)
                client.bing_projected += bing_projected_val
                if remaining > 0:
                    bing_projected_per_day = (bing_projected_val - b.current_spend) / remaining
                else:
                    bing_projected_per_day = (bing_projected_val - b.current_spend)
                for index, val in enumerate(pdays):
                    bing_projected[val.strftime('%Y-%m-%d')] = round((bing_projected_per_day * index) + b.current_spend,
                                                                     2)
                bing_p_final['B - ' + remove_accents(b.account_name) + ' Projected'] = bing_projected

                # Budget only client
                if client.has_budget and not client.has_gts:
                    bing_budget_per_day = round(b.desired_spend / last_day.day, 2)
                    for index, val in enumerate(bdays, start=1):
                        bing_budget[val.strftime('%Y-%m-%d')] = round(bing_budget_per_day * index, 2)
                    bing_b_final['B - ' + remove_accents(b.account_name) + ' Budget'] = bing_budget

                    if remaining > 0:
                        client.bing_rec_ds += (b.desired_spend - b.current_spend) / remaining
                    else:
                        client.bing_rec_ds += b.desired_spend - b.current_spend

                # GTS only client
                elif client.has_gts and not client.has_budget:
                    if remaining > 0:
                        client.bing_rec_ds += (client.target_spend - b.current_spend) / remaining
                    else:
                        client.bing_rec_ds += client.target_spend - b.current_spend
                # Both options active
                elif client.has_gts and client.has_budget:

                    if b.desired_spend > 0:
                        bing_budget_per_day = round(b.desired_spend / last_day.day, 2)
                        for index, val in enumerate(bdays, start=1):
                            bing_budget[val.strftime('%Y-%m-%d')] = round(bing_budget_per_day * index, 2)
                        bing_b_final['B - ' + remove_accents(b.account_name) + ' Budget'] = bing_budget

                        if remaining > 0:
                            client.bing_rec_ds += (b.desired_spend - b.current_spend) / remaining
                        else:
                            client.bing_rec_ds += b.desired_spend - b.current_spend
                    else:
                        if remaining > 0:
                            client.bing_rec_ds += (client.target_spend - b.current_spend) / remaining
                        else:
                            client.bing_rec_ds += client.target_spend - b.current_spend

        else:
            pass

        facebook = client.facebook.all()
        if len(facebook) > 0:
            for f in facebook:

                fb_budget, fb_spend, fb_projected = {}, {}, {}

                client.budget += f.desired_spend
                client.current_spend += f.current_spend
                client.fb_spend += f.current_spend
                client.fb_yesterday += f.yesterday_spend
                # client.fb_budget += f.desired_spend
                client.fb_current_ds += f.current_spend / today.day

                for k, v in sorted(f.segmented_spend.items()):
                    fb_temp = fb_temp + float(v)
                    fb_spend[k] = round(fb_temp, 2)
                fb_s_final['F - ' + remove_accents(f.account_name) + ' Spend'] = fb_spend

                fb_projected_val = projected(f.current_spend, f.yesterday_spend)
                client.fb_projected += fb_projected_val
                if remaining > 0:
                    fb_projected_per_day = (fb_projected_val - f.current_spend) / remaining
                else:
                    fb_projected_per_day = (fb_projected_val - f.current_spend)
                for index, val in enumerate(pdays):
                    fb_projected[val.strftime('%Y-%m-%d')] = round((fb_projected_per_day * index) + f.current_spend, 2)
                fb_p_final['F - ' + remove_accents(f.account_name) + ' Projected'] = fb_projected

                # Budget only client
                if client.has_budget and not client.has_gts:
                    fb_budget_per_day = round(f.desired_spend / last_day.day, 2)
                    for index, val in enumerate(bdays, start=1):
                        fb_budget[val.strftime('%Y-%m-%d')] = round(fb_budget_per_day * index, 2)
                    fb_b_final['F - ' + remove_accents(f.account_name) + ' Budget'] = fb_budget

                    if remaining > 0:
                        client.fb_rec_ds += (f.desired_spend - f.current_spend) / remaining
                    else:
                        client.fb_rec_ds += f.desired_spend - f.current_spend

                # GTS only client
                elif client.has_gts and not client.has_budget:
                    if remaining > 0:
                        client.fb_rec_ds += (client.target_spend - f.current_spend) / remaining
                    else:
                        client.fb_rec_ds += client.target_spend - f.current_spend
                # Both options active
                elif client.has_gts and client.has_budget:
                    if f.desired_spend > 0:
                        fb_budget_per_day = round(f.desired_spend / last_day.day, 2)
                        for index, val in enumerate(bdays, start=1):
                            fb_budget[val.strftime('%Y-%m-%d')] = round(fb_budget_per_day * index, 2)
                        fb_b_final['F - ' + remove_accents(f.account_name) + ' Budget'] = fb_budget

                        if remaining > 0:
                            client.fb_rec_ds += (f.desired_spend - f.current_spend) / remaining
                        else:
                            client.fb_rec_ds += f.desired_spend - f.current_spend

                    else:
                        if remaining > 0:
                            client.fb_rec_ds += (client.target_spend - f.current_spend) / remaining
                        else:
                            client.fb_rec_ds += client.target_spend - f.current_spend

        else:
            fb_s_final = {}
            fb_p_final = {}
            fb_b_final = {}

        client.save()

    return 'cron_clients'


@celery_app.task(bind=True)
def daily_context(self):
    """
    Replaces daily_context.py
    :param self:
    :return:
    """
    accounts = Client.objects.all()
    members = Member.objects.all()

    now = datetime.datetime.now()
    month = now.month
    year = now.year

    for account in accounts:
        # First do the allocated hours
        members = account.assigned_members

        for key in members:
            if key == 'Sold by':
                continue
            tup = members[key]
            member = tup['member']
            percentage = tup['allocated_percentage']
            allocated_hours_month = account.all_hours * (percentage / 100.0)

            record, created = AccountAllocatedHoursHistory.objects.get_or_create(account=account, member=member,
                                                                                 month=month, year=year)
            record.allocated_hours = allocated_hours_month
            record.save()

        # Do spend and budget
        account_budget_history, created = AccountBudgetSpendHistory.objects.get_or_create(account=account, month=month,
                                                                                          year=year)
        account_budget_history.aw_budget = account.aw_budget
        account_budget_history.bing_budget = account.bing_budget
        account_budget_history.fb_budget = account.fb_budget
        account_budget_history.flex_budget = account.flex_budget
        account_budget_history.aw_spend = account.aw_spend
        account_budget_history.bing_spend = account.bing_spend
        account_budget_history.fb_spend = account.fb_spend
        account_budget_history.flex_spend = account.flex_spend
        account_budget_history.management_fee = account.current_fee
        account_budget_history.status = account.status
        account_budget_history.save()

    for member in members:
        record, created = MemberHourHistory.objects.get_or_create(member=member, month=month, year=year)
        record.allocated_hours = member.allocated_hours_month
        record.actual_hours = member.actual_hours_month
        record.available_hours = member.hours_available
        record.save()

    return 'daily_context'


@celery_app.task(bind=True)
def ninety_days_update(self):
    """
    Replaces ninety_days_update.py
    :param self:
    :return:
    """
    accounts = Client.objects.all()
    for account in accounts:
        print(account.client_name + ' day was ' + str(account.phase_day))
        account.phase_day += 1
        if account.phase_day == 31:  # Should only last 30 days, therefore on the 31st day we go to new phase
            account.phase_day = 1
            if account.phase == 3:
                account.phase = 1
            else:
                account.phase += 1
        account.save()
        print(account.client_name + ' day is now ' + str(account.phase_day))

    print('done on ' + str(datetime.datetime.now()))

    for account in accounts:
        phase = account.phase
        phase_day = account.phase_day
        tier = account.tier

        tasks = PhaseTask.objects.filter(phase=phase, day=phase_day, tier=tier)
        for task in tasks:
            PhaseTaskAssignment.objects.create(task=task, account=account)
            print('created task for ' + account.client_name)
            roles = task.roles
            members_by_roles = account.members_by_roles(roles)
            members_to_assign = members_by_roles
            for member in task.members.all():
                members_to_assign.append(member)
            for member in set(members_to_assign):
                link = '/clients/accounts/' + str(account.id)
                message = account.client_name + ' task: ' + task.message
                Notification.objects.create(message=message, link=link, member=member, severity=0, type=0)

    return 'ninety_days_update'


@celery_app.task(bind=True)
def ninety_days_notifications(self):
    """
    Ninety days of awesome notifications
    :param self:
    :return:
    """
    accounts = Client.objects.filter(status=1)

    for account in accounts:
        phase = account.phase
        phase_day = account.phase_day
        tier = account.tier

        tasks = PhaseTask.objects.filter(phase=phase, day=phase_day, tier=tier)
        for task in tasks:
            PhaseTaskAssignment.objects.create(task=task, account=account)
            print('created task for ' + account.client_name)
            roles = task.roles
            members_by_roles = account.members_by_roles(roles)
            members_to_assign = members_by_roles
            for member in task.members.all():
                members_to_assign.append(member)
            for member in set(members_to_assign):
                link = '/clients/accounts/' + str(account.id)
                message = account.client_name + ' task: ' + task.message
                Notification.objects.create(message=message, link=link, member=member, severity=0, type=0)

    return 'ninety_days_notifications'


@celery_app.task(bind=True)
def update_campaigns_in_budgets(self):
    """
    Formerly campaign_groups.py
    Updates the campaigns in each budget
    :param self:
    :return:
    """
    budgets = Budget.objects.all()

    for budget in budgets:
        if settings.DEBUG:
            update_budget_campaigns(budget.id)
        else:
            update_budget_campaigns.delay(budget.id)

    return 'update_campaigns_in_budgets'


@celery_app.task(bind=True)
def update_budget_spend_history():
    """
    Updates the final spend of the month that just passed for each account
    """
    accounts = Client.objects.filter(status=1)
    now = datetime.datetime.now()
    last_month = now.date().replace(day=1) - datetime.timedelta(days=1)

    for account in accounts:
        try:
            spend_history = AccountBudgetSpendHistory.objects.get(account=account, month=last_month.month,
                                                                  year=last_month.year)
        except (AccountBudgetSpendHistory.DoesNotExist, AccountBudgetSpendHistory.MultipleObjectsReturned):
            continue

        spend_history.aw_spend = get_spend_by_account_custom_daterange(account.id, last_month.replace(day=1),
                                                                       last_month)
        spend_history.fb_spend = get_spend_by_facebook_account_custom_dates(account.id, last_month.replace(day=1),
                                                                            last_month)
        spend_history.bing_spend = get_spend_by_bing_account_custom_daterange(account.id, last_month.replace(day=1),
                                                                              last_month)
        spend_history.save()
