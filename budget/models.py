import datetime, calendar
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Sum
from adwords_dashboard import models as adwords_a
from bing_dashboard import models as bing_a
from facebook_dashboard import models as fb
from user_management.models import Member, Team
from client_area.models import Service, Industry, Language, ClientType, ClientContact, AccountHourRecord, ParentClient, ManagementFeesStructure
from dateutil.relativedelta import relativedelta
# Create your models here.


class Client(models.Model):
    """
    This should really be called 'Account' based on Bloom's business logic
    It is not worth it to refactor the database tables right now. But this class should be represented as 'Account' in any view where a user sees it
    """
    STATUS_CHOICES = [(0, 'Onboarding'),
                      (1, 'Active'),
                      (2, 'Inactive'),
                      (3, 'Lost')]

    PAYMENT_SCHEDULE_CHOICES = [(0, 'MRR'),
                                (1, 'One Time')]

    client_name = models.CharField(max_length=255, default='None')
    adwords = models.ManyToManyField(adwords_a.DependentAccount, blank=True, related_name='adwords')
    bing = models.ManyToManyField(bing_a.BingAccounts, blank=True, related_name='bing')
    facebook = models.ManyToManyField(fb.FacebookAccount, blank=True, related_name='facebook')
    current_spend = models.FloatField(default=0)
    # yesterday_spend = models.FloatField(default=0)
    aw_yesterday = models.FloatField(default=0)
    bing_yesterday = models.FloatField(default=0)
    fb_yesterday = models.FloatField(default=0)
    aw_current_ds = models.FloatField(default=0)
    bing_current_ds = models.FloatField(default=0)
    fb_current_ds = models.FloatField(default=0)
    aw_rec_ds = models.FloatField(default=0)
    bing_rec_ds = models.FloatField(default=0)
    fb_rec_ds = models.FloatField(default=0)
    aw_projected = models.FloatField(default=0)
    bing_projected = models.FloatField(default=0)
    fb_projected = models.FloatField(default=0)
    aw_spend = models.FloatField(default=0)
    bing_spend = models.FloatField(default=0)
    fb_spend = models.FloatField(default=0)
    budget = models.FloatField(default=0)
    target_spend = models.FloatField(default=0)
    has_gts = models.BooleanField(default=False)
    has_budget = models.BooleanField(default=False)
    aw_budget = models.FloatField(default=0)
    bing_budget = models.FloatField(default=0)
    fb_budget = models.FloatField(default=0)
    flex_budget = models.FloatField(default=0)
    flex_budget_start_date = models.DateTimeField(default=None, null=True, blank=True) # These are the start dates and end dates for the flex budget. Default should be this month.
    flex_budget_end_date = models.DateTimeField(default=None, null=True, blank=True)
    other_budget = models.FloatField(default=0)
    currency = models.CharField(max_length=255, default='', blank=True)

    # Parent Client (aka Client, this model should be Account)
    parentClient = models.ForeignKey(ParentClient, models.DO_NOTHING, null=True, blank=True)

    # Management Fee Structure lets you calculate the actual fee of that client
    managementFee = models.ForeignKey(ManagementFeesStructure, models.DO_NOTHING, null=True, blank=True)

    # MRR or one time
    payment_schedule = models.IntegerField(default=0, choices=PAYMENT_SCHEDULE_CHOICES)

    # override ppc hours
    allocated_ppc_override = models.FloatField(default=None, null=True, blank=True)
    # % buffer
    allocated_ppc_buffer   = models.FloatField(default=0.0)
    # management fee override
    management_fee_override = models.FloatField(default=None, null=True, blank=True)

    # The following attributes are for the client management implementation
    team           = models.ManyToManyField(Team, blank=True, related_name='team')
    industry       = models.ForeignKey(Industry, models.DO_NOTHING, null=True, related_name='industry', blank=True)
    language       = models.ManyToManyField(Language, related_name='language')
    contactInfo    = models.ManyToManyField(ClientContact, related_name='client_contact', blank=True)
    url            = models.URLField(max_length=300, null=True, blank=True)
    clientType     = models.ForeignKey(ClientType, models.DO_NOTHING, null=True, related_name='client_type', blank=True)
    tier           = models.IntegerField(default=1)
    soldBy         = models.ForeignKey(Member, models.DO_NOTHING, null=True, related_name='sold_by')
    # maybe do services another way?
    services       = models.ManyToManyField(Service, blank=True, related_name='services')
    has_seo        = models.BooleanField(default=False)
    seo_hours      = models.FloatField(default=0)
    seo_hourly_fee = models.FloatField(default=125)
    has_cro        = models.BooleanField(default=False)
    cro_hours      = models.FloatField(default=0)
    cro_hourly_fee = models.FloatField(default=125)
    status         = models.IntegerField(default=0, choices=STATUS_CHOICES)
    clientGrade    = models.IntegerField(default=0)
    actualHours    = models.IntegerField(default=0)
    star_flag      = models.BooleanField(default=False)
    target_cpa = models.FloatField(default=0)
    target_roas = models.FloatField(default=0)

    # Member attributes (we'll see if there's a better way to do this)
    cm1    = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='cm1')
    cm2    = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='cm2')
    cm3    = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='cm3')
    cmb    = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='cmb')

    am1    = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='am1')
    am2    = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='am2')
    am3    = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='am3')
    amb    = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='amb')

    seo1   = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='seo1')
    seo2   = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='seo2')
    seo3   = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='seo3')
    seob   = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='seob')

    strat1 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='strat1')
    strat2 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='strat2')
    strat3 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='strat3')
    stratb = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='stratb')

    # Allocation % of total hours
    cm1percent = models.FloatField(default=75.0)
    cm2percent = models.FloatField(default=0)
    cm3percent = models.FloatField(default=0)

    am1percent = models.FloatField(default=25.0)
    am2percent = models.FloatField(default=0)
    am3percent = models.FloatField(default=0)

    seo1percent = models.FloatField(default=0)
    seo2percent = models.FloatField(default=0)
    seo3percent = models.FloatField(default=0)

    strat1percent = models.FloatField(default=0)
    strat2percent = models.FloatField(default=0)
    strat3percent = models.FloatField(default=0)

    @property
    def calculated_tier(self):
        proj_management_fee = self.totalFee
        if proj_management_fee < 1500:
            return 3
        elif proj_management_fee < 4000:
            return 2
        else:
            return 1

    def getRemainingBudget(self):
        return self.current_budget - self.current_spend

    def getYesterdaySpend(self):
        return self.aw_yesterday + self.bing_yesterday + self.fb_yesterday

    def getHoursWorkedThisMonth(self):
        if not hasattr(self, '_hours_worked_this_month'):
            now   = datetime.datetime.now()
            month = now.month
            year  = now.year
            hours = AccountHourRecord.objects.filter(account=self, month=month, year=year, is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
            self._hours_worked_this_month = hours if hours != None else 0
        return self._hours_worked_this_month

    def getHoursRemainingThisMonth(self):
        # Cache this because its calls DB stuff
        if not hasattr(self, '_hoursRemainingMonth'):
            self._hoursRemainingMonth = round(self.getAllocatedHours() - self.getHoursWorkedThisMonth(), 2)
        return self._hoursRemainingMonth

    def getHoursWorkedThisMonthMember(self, member):
        now   = datetime.datetime.now()
        month = now.month
        year  = now.year
        hours = AccountHourRecord.objects.filter(member=member, account=self, month=month, year=year, is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
        return hours if hours != None else 0

    @property
    def google_kpi_month(self):
        """
        Returns google ads kpi info this month
        """
        if not hasattr(self, '_google_cpa_month'):
            kpid = {}
            conversions = 0.0
            cost = 0.0
            conversion_value = 0.0

            for aa in self.adwords.all():
                aw_perf = adwords_a.Performance.objects.filter(account=aa, performance_type='ACCOUNT')
                recent_perf = aw_perf[0].metadata if aw_perf else {}
                if 'vals' in recent_perf and 'conversions' in recent_perf['vals'] and 'cost' in recent_perf['vals']: # We have CPA info
                    conversions += float(recent_perf['vals']['conversions'][1])
                    cost += float(recent_perf['vals']['cost'][1]) / 1000000.0
                kpid['roas'] = 0.0
                if 'vals' in recent_perf and 'all_conv_value' in recent_perf['vals']:
                    conversion_value += float(recent_perf['vals']['all_conv_value'][1])

            kpid['conversions'] = conversions
            kpid['cost'] = cost
            kpid['conversion_value'] = conversion_value

            try:
                kpid['cpa'] = cost / conversions
            except:
                kpid['cpa'] = 0.0

            try:
                kpid['roas'] = conversion_value / cost
            except:
                kpid['roas'] = 0.0

            self._google_cpa_month = kpid
        return self._google_cpa_month

    @property
    def facebook_kpi_month(self):
        """
        Returns facebook ads kpi info this month
        """
        if not hasattr(self, '_facebook_cpa_month'):
            kpid = {}
            conversions = 0.0
            cost = 0.0
            conversion_value = 0.0

            for fa in self.facebook.all():
                fb_perf = fb.FacebookPerformance.objects.filter(account=fa, performance_type='ACCOUNT')
                recent_perf = fb_perf[0].metadata if fb_perf else {}
                if 'vals' in recent_perf and 'conversions' in recent_perf['vals'] and 'spend' in recent_perf['vals']: # We have CPA info
                    conversions += float(recent_perf['vals']['conversions'][1])
                    cost += float(recent_perf['vals']['spend'][1]) / 1000000.0
                kpid['roas'] = 0.0
                if 'vals' in recent_perf and 'all_conv_value' in recent_perf['vals']: # we have conversion value info
                    conversion_value += float(recent_perf['vals']['all_conv_value'][1]) # TODO: it's not called this in facebook ads

            kpid['conversions'] = conversions
            kpid['cost'] = cost
            kpid['conversion_value'] = conversion_value

            try:
                kpid['cpa'] = cost / conversions
            except:
                kpid['cpa'] = 0.0

            try:
                kpid['roas'] = conversion_value / cost
            except:
                kpid['roas'] = 0.0

            self._facebook_cpa_month = kpid
        return self._facebook_cpa_month

    @property
    def kpi_info(self):
        """
        Returns a dict with both the KPI string and the value (only adwords for beta)
        """
        """
        Example output from adwords performance object
        In all arrays, 0 is diff, 1 is now, 2 is previous
        {'vals': {'ctr': [-13.391984359726287, '10.23%', '11.60%'], 'cost': [14.090268386064498, '2099960000', '1804070000'],
        'clicks': [-13.098134630981345, '2466', '2789'],
        'avg_cpc': [24.039621168084643, '851565', '646852'], 'cost__conv': [0.9137399904610828, '32534091', '32236814'],
        'client_name': ['AbbVie - HS', 'AbbVie - HS', 'AbbVie - HS'], 'conversions': [13.307513555383418, '64.55', '55.96'],
        'customer_id': ['8156310238', '8156310238', '8156310238'], 'impressions': [0.31927685864742716, '24117', '24040'],
        'all_conv_value': [0.0, '0.00', '0.00'], 'search_impr_share': [1.7761989342806417, '61.93%', '60.83%']},
        'daterange1_max': '20181120', 'daterange1_min': '20181101', 'daterange2_max': '20181020', 'daterange2_min': '20181001'}
        """
        if not hasattr(self, '_kpi_info'):
            kpid = {}

            conversions = 0.0
            cost = 0.0
            final_cpa = 0.0

            total_add_spend = 0.0
            total_conversion_value = 0.0
            roas = 0.0

            """
            Parse adwords performance object
            """
            # for aa in self.adwords.all():
            #     aw_perf = adwords_a.Performance.objects.filter(account=aa, performance_type='ACCOUNT')
            #     recent_perf = aw_perf[0].metadata if aw_perf else {}
            #     if 'vals' in recent_perf and 'conversions' in recent_perf['vals'] and 'cost' in recent_perf['vals']: # We have CPA info
            #         conversions += float(recent_perf['vals']['conversions'][1])
            #         cost += float(recent_perf['vals']['cost'][1]) / 1000000.0

            conversions += self.google_kpi_month['conversions']
            cost += self.google_kpi_month['cost']
            total_conversion_value += self.google_kpi_month['conversion_value']

            """
            Facebook
            """
            # for fa in self.facebook.all():
            #     fb_perf = fb.FacebookPerformance.objects.filter(account=fa, performance_type='ACCOUNT')
            #     recent_perf = fb_perf[0].metadata if fb_perf else {}
            #     if 'vals' in recent_perf and 'conversions' in recent_perf['vals'] and 'spend' in recent_perf['vals']: # We have CPA info
            #         conversions += float(recent_perf['vals']['conversions'][1])
            #         cost += float(recent_perf['vals']['spend'][1]) / 1000000.0

            conversions += self.facebook_kpi_month['conversions']
            cost += self.facebook_kpi_month['cost']
            total_conversion_value += self.facebook_kpi_month['conversion_value']

            # """
            # Parse Bing performance object
            # """
            # for ba in self.bing.all():
            #     bing_perf = bing_a.BingAnomalies.objects.filter(account=ba, performance_type='ACCOUNT')
            #     recent_perf = bing_perf[0] if bing_perf else {}
            #     conversions += float(recent_perf.conversions)
            #     cost += float(recent_perf.cost)

            try:
                final_cpa = cost / conversions
            except:
                final_cpa = 0.0
            kpid['cpa'] = final_cpa

            try:
                kpid['roas'] = total_conversion_value / cost
            except:
                kpid['roas'] = 0.0


            if len(kpid) == 0:
                self._kpi_info = kpid
                return self._kpi_info

            # kpid['cpa'] = 0.0
            # if 'cost__conv' in kpid['kpi']['vals']:
            #     kpid['cpa'] = float(kpid['kpi']['vals']['cost__conv'][1]) / 1000000.0
            #
            # kpid['roas'] = 0.0
            # if 'all_conv_value' in kpid['kpi']['vals']:
            #     kpid['roas'] = float(kpid['kpi']['vals']['all_conv_value'][1]) / (float(kpid['kpi']['vals']['cost'][1]) / 1000000.0)

            self._kpi_info = kpid
        return self._kpi_info

    @property
    def cpa_this_month(self):
        """
        TODO: Needs to be improved
        """
        return self.kpi_info['cpa']

    @property
    def roas_this_month(self):
        """
        TODO: Needs to be improved
        """
        return self.kpi_info['roas']

    @property
    def value_added_hours_this_month(self):
        if not hasattr(self, '_value_added_hours_this_month'):
            now   = datetime.datetime.now()
            hours = AccountHourRecord.objects.filter(account=self, month=now.month, year=now.year, is_unpaid=True).aggregate(Sum('hours'))['hours__sum']
            self._value_added_hours_this_month = hours if hours != None else 0
        return self._value_added_hours_this_month


    def value_added_hours_month_member(self, member):
        now   = datetime.datetime.now()
        hours = AccountHourRecord.objects.filter(member=member, account=self, month=now.month, year=now.year, is_unpaid=True).aggregate(Sum('hours'))['hours__sum']
        return hours if hours != None else 0


    def getAllocationThisMonthMember(self, member):
        percentage = 0.0
        # Boilerplate incoming
        if (self.cm1 == member):
            percentage += self.cm1percent
        if (self.cm2 == member):
            percentage += self.cm2percent
        if (self.cm3 == member):
            percentage += self.cm3percent
        if (self.am1 == member):
            percentage += self.am1percent
        if (self.am2 == member):
            percentage += self.am2percent
        if (self.am3 == member):
            percentage += self.am3percent
        if (self.seo1 == member):
            percentage += self.seo1percent
        if (self.seo2 == member):
            percentage += self.seo2percent
        if (self.seo3 == member):
            percentage += self.seo3percent
        if (self.strat1 == member):
            percentage += self.strat1percent
        if (self.strat2 == member):
            percentage += self.strat2percent
        if (self.strat3 == member):
            percentage += self.strat3percent

        return round(self.getAllocatedHours() * percentage / 100.0, 2)


    def getSeoFee(self):
        """
        Get's the SEO fee
        """
        fee = 0.0
        if (self.has_seo):
            fee += self.seo_hours * self.seo_hourly_fee
        return fee

    def getCroFee(self):
        """
        Get's the CRO fee
        """
        fee = 0.0
        if (self.has_cro):
            fee += self.cro_hours * self.cro_hourly_fee
        return fee

    def getPpcFee(self):
        """
        Loops through every interval in the management fee structure, determines
        """
        if not hasattr(self, '_ppcFee'):
            fee = self.get_fee_by_spend(self.current_budget)
            # if (self.management_fee_override != None and self.management_fee_override != 0.0):
            #     fee = self.management_fee_override
            # elif (self.managementFee != None):
                # for feeInterval in self.managementFee.feeStructure.all().order_by('lowerBound'):
                #     if (self.current_budget >= feeInterval.lowerBound and self.current_budget < feeInterval.upperBound):
                #         if (feeInterval.feeStyle == 0): # %
                #             fee = self.current_budget * (feeInterval.fee / 100.0)
                #             break
                #         elif (feeInterval.feeStyle == 1):
                #             fee = feeInterval.fee
                #             break
            self._ppcFee = round(fee, 2)
        return self._ppcFee

    def get_fee_by_spend(self, spend):
        """
        Get's fee by any amount, as opposed to just calculating it by budget
        It is calculated by budget for anticipated fee, but actual fee or projected fee can be calculated using this as well
        """
        fee = 0.0
        if (self.management_fee_override != None and self.management_fee_override != 0.0):
            fee = self.management_fee_override
        elif (self.managementFee != None):
            for feeInterval in self.managementFee.feeStructure.all().order_by('lowerBound'):
                if (spend >= feeInterval.lowerBound and spend <= feeInterval.upperBound):
                    if (feeInterval.feeStyle == 0): # %
                        fee = spend * (feeInterval.fee / 100.0)
                        break
                    elif (feeInterval.feeStyle == 1):
                        fee = feeInterval.fee
                        break
        return fee

    def getFee(self):
        if (self.management_fee_override != None and self.management_fee_override != 0.0):
            fee = self.management_fee_override
        else:
            fee = self.getPpcFee() + self.getCroFee() + self.getSeoFee()
        return fee

    def getPpcAllocatedHours(self):
        if (self.allocated_ppc_override != None and self.allocated_ppc_override != 0.0):
            unrounded = self.allocated_ppc_override
        else:
            unrounded = (self.getPpcFee() / 125.0)  * ((100.0 - self.allocated_ppc_buffer) / 100.0)
        return round(unrounded, 2)

    def getAllocatedHours(self):
        hours = self.getPpcAllocatedHours()
        if (self.has_seo):
            hours += self.seo_hours
        if (self.has_cro):
            hours += self.cro_hours
        return round(hours, 2)


    def days_in_month_in_daterange(self, start, end, month):
        """
        Calculates how many days are in a certain month within a daterange. For example: October 28th to November 5th has 4 days in October, so this would return 4 for (2018-10-28, 2018-11-05, 10)
        """
        one_day = datetime.timedelta(1)
        date_counter = 0
        cur_date = start
        while cur_date <= end:
            if cur_date.month == month:
                date_counter += 1
            elif cur_date.month > month:
                break
            cur_date = cur_date + one_day

        return date_counter


    @property
    def adwords_budget_this_month(self):
        if not hasattr(self, '_adwords_budget_this_month'):
            budget = 0.0
            yesterday = datetime.datetime.now() - datetime.timedelta(1)  # We should really be getting yesterday's budget
            for aa in self.adwords.all():
                if (aa.has_custom_dates):
                    """
                    If there are custom dates, we need to get the portion of the budget that is in this month
                    """
                    portion_of_spend = self.days_in_month_in_daterange(aa.desired_spend_start_date, aa.desired_spend_end_date, yesterday.month) / (aa.desired_spend_end_date - aa.desired_spend_start_date).days
                    budget += round(portion_of_spend * aa.desired_spend, 2)
                else:
                    budget += aa.desired_spend # this would be monthly budget
            self._adwords_budget_this_month = budget
        return self._adwords_budget_this_month


    @property
    def one_contact(self):
        """
        Just returns the first contact
        """
        if (self.contactInfo.all().count() == 0):
            return None
        return self.contactInfo.all()[0]


    @property
    def bing_budget_this_month(self):
        if not hasattr(self, '_bing_budget_this_month'):
            budget = 0.0
            yesterday = datetime.datetime.now() - datetime.timedelta(1)  # We should really be getting yesterday's budget
            for ba in self.bing.all():
                if (ba.has_custom_dates):
                    """
                    If there are custom dates, we need to get the portion of the budget that is in this month
                    """
                    portion_of_spend = self.days_in_month_in_daterange(ba.desired_spend_start_date, ba.desired_spend_end_date, yesterday.month) / (ba.desired_spend_end_date - ba.desired_spend_start_date).days
                    budget += round(portion_of_spend * ba.desired_spend, 2)
                else:
                    budget += ba.desired_spend # this would be monthly budget
            self._bing_budget_this_month = budget
        return self._bing_budget_this_month


    @property
    def facebook_budget_this_month(self):
        if not hasattr(self, '_facebook_budget_this_month'):
            budget = 0.0
            yesterday = datetime.datetime.now() - datetime.timedelta(1)  # We should really be getting yesterday's budget
            for fa in self.facebook.all():
                if (fa.has_custom_dates):
                    """
                    If there are custom dates, we need to get the portion of the budget that is in this month
                    """
                    portion_of_spend = self.days_in_month_in_daterange(fa.desired_spend_start_date, fa.desired_spend_end_date, yesterday.month) / (fa.desired_spend_end_date - fa.desired_spend_start_date).days
                    budget += round(portion_of_spend * fa.desired_spend, 2)
                else:
                    budget += fa.desired_spend # this would be monthly budget
            self._facebook_budget_this_month = budget
        return self._facebook_budget_this_month


    def getCurrentBudget(self):
        if not hasattr(self, '_current_budget'):
            budget = 0.0
            budget += self.adwords_budget_this_month
            budget += self.bing_budget_this_month
            budget += self.facebook_budget_this_month

            budget += self.flex_budget
            self._current_budget = budget

        return self._current_budget

    def getCurrentFullBudget(self):
        return self.getCurrentBudget() + self.other_budget

    def getFlexSpendThisMonth(self):
        flex_spend = 0.0
        if (self.aw_spend > self.aw_budget):
            flex_spend += (self.aw_spend - self.aw_budget)
        if (self.fb_spend > self.fb_budget):
            flex_spend += (self.fb_spend - self.fb_budget)
        if (self.bing_spend > self.bing_budget):
            flex_spend += (self.bing_spend - self.bing_budget)

        return flex_spend


    @property
    def utilization_rate_this_month(self):
        """
        Gets the utilization rate this month as percentage (100 * actual / allocated)
        """
        if self.allHours == 0:
            return 0.0
        return 100 * self.hoursWorkedThisMonth / self.allHours

    @property
    def projected_loss(self):
        fee_if_budget_spent = self.ppcFee
        fee_if_projected_spent = self.get_fee_by_spend(self.project_yesterday)
        return round(fee_if_budget_spent - fee_if_projected_spent, 2)


    @property
    def has_adwords(self):
        return self.adwords != None


    @property
    def has_bing(self):
        return self.bing != None


    @property
    def has_fb(self):
        return self.facebook != None


    @property
    def assigned_ams(self):
        """
        Get's assigned ams
        """
        members = {}

        if (self.am1 != None):
            members['AM'] = {}
            members['AM']['member'] = self.am1
            members['AM']['allocated_percenage'] = self.am1percent
        if (self.am2 != None):
            members['AM2'] = {}
            members['AM2']['member'] = self.am2
            members['AM2']['allocated_percenage'] = self.am2percent
        if (self.am3 != None):
            members['AM3'] = {}
            members['AM3']['member'] = self.am3
            members['AM3']['allocated_percenage'] = self.am3percent
        if (self.amb != None):
            members['AMB'] = {}
            members['AMB']['member'] = self.amb

        return members


    @property
    def assigned_cms(self):
        """
        Get's assigned cms
        """
        members = {}

        if (self.cm1 != None):
            members['CM'] = {}
            members['CM']['member'] = self.cm1
            members['CM']['allocated_percenage'] = self.cm1percent
        if (self.cm2 != None):
            members['CM2'] = {}
            members['CM2']['member'] = self.cm2
            members['CM2']['allocated_percenage'] = self.cm2percent
        if (self.cm3 != None):
            members['CM3'] = {}
            members['CM3']['member'] = self.cm3
            members['CM3']['allocated_percenage'] = self.cm3percent
        if (self.cmb != None):
            members['CMB'] = {}
            members['CMB']['member'] = self.cmb

        return members


    @property
    def assigned_seos(self):
        """
        Get's assigned seos
        """
        members = {}

        if (self.seo1 != None):
            members['SEO'] = {}
            members['SEO']['member'] = self.seo1
            members['SEO']['allocated_percenage'] = self.seo1percent
        if (self.seo2 != None):
            members['SEO 2'] = {}
            members['SEO 2']['member'] = self.seo2
            members['SEO 2']['allocated_percenage'] = self.seo2percent
        if (self.seo3 != None):
            members['SEO 3'] = {}
            members['SEO 3']['member'] = self.seo3
            members['SEO 3']['allocated_percenage'] = self.seo3percent
        if (self.seob != None):
            members['SEOB'] = {}
            members['SEOB']['member'] = self.seob

        return members


    @property
    def assigned_strats(self):
        """
        Get's assigned strats
        """
        members = {}

        if (self.strat1 != None):
            members['Strat'] = {}
            members['Strat']['member'] = self.strat1
            members['Strat']['allocated_percenage'] = self.strat1percent
        if (self.strat2 != None):
            members['Strat 2'] = {}
            members['Strat 2']['member'] = self.strat2
            members['Strat 2']['allocated_percenage'] = self.strat2percent
        if (self.strat3 != None):
            members['Strat 3'] = {}
            members['Strat 3']['member'] = self.strat3
            members['Strat 3']['allocated_percenage'] = self.strat3percent
        if (self.stratb != None):
            members['Strat B'] = {}
            members['Strat B']['member'] = self.stratb

        return members


    @property
    def assigned_members(self):
        """
        Get's members assigned to the account in a dictionary with role as key and member as value
        """
        members = {}

        if (self.cm1 != None):
            members['CM'] = {}
            members['CM']['member'] = self.cm1
            members['CM']['allocated_percenage'] = self.cm1percent
        if (self.cm2 != None):
            members['CM2'] = {}
            members['CM2']['member'] = self.cm2
            members['CM2']['allocated_percenage'] = self.cm2percent
        if (self.cm3 != None):
            members['CM3'] = {}
            members['CM3']['member'] = self.cm3
            members['CM3']['allocated_percenage'] = self.cm3percent
        # if (self.cmb != None):
        #     members['CM Backup'] = {}
        #     members['CM Backup']['member'] = self.cmb
        #     members['CM Backup']['allocated_percenage'] = self.cmbpercent

        if (self.am1 != None):
            members['AM'] = {}
            members['AM']['member'] = self.am1
            members['AM']['allocated_percenage'] = self.am1percent
        if (self.am2 != None):
            members['AM2'] = {}
            members['AM2']['member'] = self.am2
            members['AM2']['allocated_percenage'] = self.am2percent
        if (self.am3 != None):
            members['AM3'] = {}
            members['AM3']['member'] = self.am3
            members['AM3']['allocated_percenage'] = self.am3percent
        # if (self.amb != None):
        #     members['AM Backup'] = {}
        #     members['AM Backup']['member'] = self.amb
        #     members['AM Backup']['allocated_percenage'] = self.ambpercent

        if (self.seo1 != None):
            members['SEO'] = {}
            members['SEO']['member'] = self.seo1
            members['SEO']['allocated_percenage'] = self.seo1percent
        if (self.seo2 != None):
            members['SEO 2'] = {}
            members['SEO 2']['member'] = self.seo2
            members['SEO 2']['allocated_percenage'] = self.seo2percent
        if (self.seo3 != None):
            members['SEO 3'] = {}
            members['SEO 3']['member'] = self.seo3
            members['SEO 3']['allocated_percenage'] = self.seo3percent
        # if (self.seob != None):
        #     members['SEO Backup'] = {}
        #     members['SEO Backup']['member'] = self.seob
        #     members['SEO Backup']['allocated_percenage'] = self.seobpercent

        if (self.strat1 != None):
            members['Strat'] = {}
            members['Strat']['member'] = self.strat1
            members['Strat']['allocated_percenage'] = self.strat1percent
        if (self.strat2 != None):
            members['Strat 2'] = {}
            members['Strat 2']['member'] = self.strat2
            members['Strat 2']['allocated_percenage'] = self.strat2percent
        if (self.strat3 != None):
            members['Strat 3'] = {}
            members['Strat 3']['member'] = self.strat3
            members['Strat 3']['allocated_percenage'] = self.strat3percent
        # if (self.stratb != None):
        #     members['Strat Backup'] = {}
        #     members['Strat Backup']['member'] = self.stratb
        #     members['Strat Backup']['allocated_percenage'] = self.stratbpercent

        return members


    @property
    def team_leads(self):
        team_leads = Member.objects.none()
        for team in self.team.all():
            team_leads = team_leads | team.team_lead
        return team_leads


    @property
    def project_average(self):
        return self.hybrid_projection(1)


    @property
    def project_yesterday(self):
        return self.hybrid_projection(0)


    def hybrid_projection(self, method):
        projection = self.current_spend
        now = datetime.datetime.today() - datetime.timedelta(1)
        day_of_month = now.day
        # day_of_month = now.day - 1
        f, days_in_month = calendar.monthrange(now.year, now.month)
        days_remaining = days_in_month - day_of_month
        if (method == 0): # Project based on yesterday
            projection += (self.yesterday_spend * days_remaining)
        elif (method == 1):
            projection += ((self.current_spend / day_of_month) * days_remaining)

        return projection

    # Recommended daily spend for clients with flex budget
    # TODO: If no flex budget is set, calculate the rec ds as in cron_clients.py
    def rec_ds(self):

        today = datetime.date.today() - relativedelta(days=1)
        last_day = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

        remaining = last_day.day - today.day

        rec_ds = 0

        if self.flex_budget > 0:
            if remaining != 0:
                rec_ds = (self.flex_budget - self.flex_spend) / remaining

        return rec_ds

    remainingBudget = property(getRemainingBudget)

    yesterday_spend = property(getYesterdaySpend)
    # recommended daily spend
    rec_ds          = property(rec_ds)

    hoursWorkedThisMonth = property(getHoursWorkedThisMonth)
    hoursRemainingMonth  = property(getHoursRemainingThisMonth)

    seoFee   = property(getSeoFee)
    croFee   = property(getCroFee)
    ppcFee   = property(getPpcFee)
    totalFee = property(getFee)
    ppcHours = property(getPpcAllocatedHours)
    allHours = property(getAllocatedHours)

    current_budget = property(getCurrentBudget)
    current_full_budget = property(getCurrentFullBudget)

    flex_spend = property(getFlexSpendThisMonth)

    def __str__(self):
        return self.client_name


class AccountBudgetSpendHistory(models.Model):
    """
    Keeps historical data for client budget and spend
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1,13)]

    account = models.ForeignKey(Client, models.DO_NOTHING, blank=True, null=True)
    month = models.IntegerField(choices=MONTH_CHOICES, default=1)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    management_fee = models.FloatField(default=0.0)
    aw_budget = models.FloatField(default=0)
    bing_budget = models.FloatField(default=0)
    fb_budget = models.FloatField(default=0)
    flex_budget = models.FloatField(default=0)
    aw_spend = models.FloatField(default=0)
    bing_spend = models.FloatField(default=0)
    fb_spend = models.FloatField(default=0)
    flex_spend = models.FloatField(default=0)

    @property
    def budget(self):
        return self.aw_budget + self.bing_budget + self.fb_budget + self.flex_budget

    @property
    def spend(self):
        return self.aw_spend + self.bing_spend + self.fb_spend + self.bing_spend


class BudgetUpdate(models.Model):
    """
    TEMPORARY SOLUTION: Record of if a budget has been updated this month
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1,13)]

    account = models.ForeignKey(Client, models.DO_NOTHING, blank=True, null=True)
    updated = models.BooleanField(default=False)
    month = models.IntegerField(choices=MONTH_CHOICES, default=1)
    year = models.PositiveSmallIntegerField(blank=True, null=True)



class ClientCData(models.Model):

    client = models.ForeignKey(Client, models.DO_NOTHING, blank=True, null=True)
    aw_budget = JSONField(default=dict)
    aw_projected = JSONField(default=dict)
    aw_spend = JSONField(default=dict)
    bing_budget = JSONField(default=dict)
    bing_projected = JSONField(default=dict)
    bing_spend = JSONField(default=dict)
    fb_budget = JSONField(default=dict)
    fb_projected = JSONField(default=dict)
    fb_spend = JSONField(default=dict)
    global_target_spend = JSONField(default=dict)


class ClientHist(models.Model):

    client_name = models.CharField(max_length=255, default='None')
    hist_adwords = models.ManyToManyField(adwords_a.DependentAccount, blank=True, related_name='hist_adwords')
    hist_bing = models.ManyToManyField(bing_a.BingAccounts, blank=True, related_name='hist_bing')
    hist_facebook = models.ManyToManyField(fb.FacebookAccount, blank=True, related_name='hist_facebook')
    hist_spend = models.FloatField(default=0)
    hist_aw_spend = models.FloatField(default=0)
    hist_bing_spend = models.FloatField(default=0)
    hist_fb_spend = models.FloatField(default=0)
    hist_budget = models.FloatField(default=0)
    hist_aw_budget = models.FloatField(default=0)
    hist_bing_budget = models.FloatField(default=0)
    hist_fb_budget = models.FloatField(default=0)


class FlightBudget(models.Model):

    budget = models.FloatField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    current_spend = models.FloatField(default=0)
    adwords_account = models.ForeignKey(adwords_a.DependentAccount, models.DO_NOTHING, blank=True, null=True)
    bing_account = models.ForeignKey(bing_a.BingAccounts, models.DO_NOTHING, blank=True, null=True)
    facebook_account = models.ForeignKey(fb.FacebookAccount, models.DO_NOTHING, blank=True, null=True)


class CampaignGrouping(models.Model):

    client = models.ForeignKey(Client, models.DO_NOTHING, blank=True, null=True)
    group_name = models.CharField(max_length=255, default='')
    group_by = models.CharField(max_length=255, default='')
    adwords = models.ForeignKey(adwords_a.DependentAccount, models.DO_NOTHING, blank=True, null=True)
    aw_campaigns = models.ManyToManyField(adwords_a.Campaign, blank=True, related_name='aw_campaigns')
    aw_spend = models.FloatField(default=0)
    aw_yspend = models.FloatField(default=0)
    bing_campaigns = models.ManyToManyField(bing_a.BingCampaign, blank=True, related_name='bing_campaigns')
    bing_spend = models.FloatField(default=0)
    bing_yspend = models.FloatField(default=0)
    fb_campaigns = models.ManyToManyField(fb.FacebookCampaign, blank=True, related_name='facebook_campaigns')
    fb_spend = models.FloatField(default=0)
    fb_yspend = models.FloatField(default=0)
    budget = models.FloatField(default=0)
    adwords = models.ForeignKey(adwords_a.DependentAccount, models.DO_NOTHING, blank=True, null=True)
    bing = models.ForeignKey(bing_a.BingAccounts, models.DO_NOTHING, blank=True, null=True)
    facebook = models.ForeignKey(fb.FacebookAccount, models.DO_NOTHING, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def current_spend(self):
        return self.aw_spend + self.bing_spend + self.fb_spend

    def yesterday_spend(self):
        return self.aw_yspend + self.bing_yspend + self.fb_yspend

    def rec_daily_spend(self):
        now = datetime.datetime.today()
        day_of_month = now.day - 1
        f, days_in_month = calendar.monthrange(now.year, now.month)
        days_remaining = days_in_month - day_of_month

        answer = 0
        if days_remaining != 0:
            answer = (self.budget - self.current_spend) / days_remaining

        return answer

    def avg_daily_spend(self):
        now = datetime.datetime.today() - datetime.timedelta(1)
        day_of_month = now.day
        return self.current_spend / day_of_month

    @property
    def project_average(self):
        return self.hybrid_projection(1)

    @property
    def project_yesterday(self):
        return self.hybrid_projection(0)


    def hybrid_projection(self, method):
        projection = self.current_spend
        now = datetime.datetime.today() - datetime.timedelta(1)
        day_of_month = now.day
        f, days_in_month = calendar.monthrange(now.year, now.month)
        days_remaining = days_in_month - day_of_month
        if (method == 0): # Project based on yesterday
            projection += (self.yesterday_spend * days_remaining)
        elif (method == 1):
            projection += ((self.current_spend / day_of_month) * days_remaining)

        return projection

    yesterday_spend = property(yesterday_spend)
    avg_daily_spend = property(avg_daily_spend)
    rec_daily_spend = property(rec_daily_spend)
    current_spend = property(current_spend)


class Budget(models.Model):

    adwords = models.ForeignKey(adwords_a.DependentAccount, models.DO_NOTHING, blank=True, null=True)
    budget = models.FloatField(default=0)
    # client = models.ForeignKey(Client, related_name='client')
    network_type = models.CharField(max_length=255, default='ALL')
    networks = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    spend = models.FloatField(default=0)


class TierChangeProposal(models.Model):
    """
    Tier change proposed by budget or management fee change
    """

    account = models.ForeignKey(Client, models.DO_NOTHING, blank=True, null=True, default=None)
    tier_from = models.IntegerField(default=0)
    tier_to = models.IntegerField(default=0)
    fee_from = models.FloatField(default=0.0)
    fee_to = models.FloatField(default=0.0)
    changed = models.BooleanField(default=False)
    changed_by = models.ForeignKey('user_management.Member', models.DO_NOTHING, blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
