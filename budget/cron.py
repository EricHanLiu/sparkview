from bloom import celery_app, settings
from adwords_dashboard.models import Campaign
from facebook_dashboard.models import FacebookCampaign
from bing_dashboard.models import BingCampaign
from budget.models import Budget, Client


def reset_all_campaign_spends():
    adwords_cmps = Campaign.objects.all()

    for cmp in adwords_cmps:
        if settings.DEBUG:
            reset_google_ads_campaign(cmp.id)
        else:
            reset_google_ads_campaign.delay(cmp.id)

    fb_cmps = FacebookCampaign.objects.all()

    for cmp in fb_cmps:
        if settings.DEBUG:
            reset_facebook_campaign(cmp.id)
        else:
            reset_facebook_campaign.delay(cmp.id)

    bing_cmps = BingCampaign.objects.all()

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

    print('Resetting adwords campaign: ' + str(cmp))
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

    print('Resetting adwords campaign: ' + str(cmp))
    cmp.campaign_yesterday_cost = 0
    cmp.spend_until_yesterday = 0
    cmp.campaign_cost = 0
    cmp.save()


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
        create_default_budget.delay(account.id)

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
