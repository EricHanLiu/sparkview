cur_month = 10
cur_year = 2019
for i in range(24):
    aggregate_spend = 0.0
    aggregate_fee = 0.0
    for account in Client.objects.all():
        tmpd = {}
        try:
            bh = AccountBudgetSpendHistory.objects.get(month=cur_month, year=cur_year, account=account)
            tmpd['fee'] = round(bh.management_fee, 2)
            tmpd['spend'] = round(bh.spend, 2)
        except AccountBudgetSpendHistory.DoesNotExist:
            tmpd['fee'] = 0.0
            tmpd['spend'] = 0.0
        aggregate_spend += tmpd['spend']
        aggregate_fee += tmpd['fee']
    MemberDashboardSnapshot.objects.create(month=cur_month, year=cur_year, aggregate_spend=aggregate_spend,
                                               aggregate_fee=aggregate_fee)
    cur_month -= 1
    if cur_month == 0:
        cur_month = 12
        cur_year -= 1
