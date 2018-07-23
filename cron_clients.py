import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from budget.models import Client, ClientCData
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta

def projected(spend):

    today = datetime.today() - relativedelta(days=1)
    d_spend = spend / today.day
    next_month = datetime(
        year=today.year,
        month=((today.month + 1) % 12),
        day=1
    )
    lastday_month = next_month + relativedelta(days=-1)
    remaining = lastday_month.day - today.day

    # projected value
    rval = spend + (d_spend * remaining)

    return round(rval ,2)

def main():

    today = date.today() - relativedelta(days=1)
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, 1) + relativedelta(months=1, days=-1)

    pdays = []
    bdays = []

    for result in perdelta(today, last_day, timedelta(days=1)):
        pdays.append(result)

    for result in perdelta(first_day, last_day, timedelta(days=1)):
        bdays.append(result)

    aw_budget = {}
    aw_spend = {}
    aw_projected = {}
    bing_budget = {}
    bing_spend = {}
    bing_projected = {}
    fb_budget = {}
    fb_spend = {}
    fb_projected = {}

    clients = Client.objects.all()

    for client in clients:

        new_client_cdata, created = ClientCData.objects.get_or_create(client=client)
        aw_temp = 0.0
        b_temp = 0.0
        fb_temp = 0.0

        client.budget = 0
        client.current_spend = 0
        client.aw_spend = 0
        client.bing_spend = 0
        client.fb_spend = 0
        client.aw_budget = 0
        client.bing_budget = 0
        client.fb_budget = 0
        client.yesterday_spend = 0
        client.save()

        adwords = client.adwords.all()
        if len(adwords) > 0:
            for a in adwords:
                client.budget += a.desired_spend
                client.current_spend += a.current_spend
                client.aw_spend += a.current_spend
                client.yesterday_spend += a.yesterday_spend
                client.aw_budget += a.desired_spend

                for k, v in sorted(a.segmented_spend.items()):
                    if v['cost'] == 0:
                        aw_temp = aw_temp + float(v['cost'])
                    else:
                        aw_temp = aw_temp + float(int(v['cost']) / 1000000)
                    aw_spend[v['day']] = round(aw_temp, 2)

                aw_projected_val = projected(client.aw_spend)
                aw_projected_per_day = aw_projected_val / last_day.day
                for index, val in enumerate(pdays):
                    aw_projected[val.strftime("%Y-%m-%d")] = round((aw_projected_per_day * index) + a.current_spend, 2)

                aw_budget_per_day = round(client.aw_budget / last_day.day, 2)
                for index, val in enumerate(bdays, start=1):
                    aw_budget[val.strftime("%Y-%m-%d")] = round(aw_budget_per_day * index, 2)
        else:
            aw_spend = {}
            aw_budget = {}
            aw_projected = {}

        bing = client.bing.all()
        if len(bing) > 0:
            for b in bing:
                client.budget += b.desired_spend
                client.current_spend += b.current_spend
                client.bing_spend += b.current_spend
                client.yesterday_spend += b.yesterday_spend
                client.bing_budget += b.desired_spend

                for k, v in sorted(b.segmented_spend.items()):
                    b_temp = b_temp + float(v['spend'])
                    bing_spend[v['gregoriandate']] = round(b_temp, 2)

                bing_projected_val = projected(client.bing_spend)
                bing_projected_per_day = bing_projected_val / last_day.day
                for index, val in enumerate(pdays):
                    bing_projected[val.strftime("%Y-%m-%d")] = round((bing_projected_per_day * index) + b.current_spend, 2)

                bing_budget_per_day = round(client.bing_budget / last_day.day, 2)
                for index, val in enumerate(bdays, start=1):
                    bing_budget[val.strftime("%Y-%m-%d")] = round(bing_budget_per_day * index, 2)

        else:
            bing_spend = {}
            bing_projected = {}
            bing_budget = {}


        facebook = client.facebook.all()
        if len(facebook) > 0:
            for f in facebook:
                client.budget += f.desired_spend
                client.current_spend += f.current_spend
                client.fb_spend += f.current_spend
                client.yesterday_spend += f.yesterday_spend
                client.fb_budget += f.desired_spend

                for k, v in sorted(f.segmented_spend.items()):
                    fb_temp = fb_temp + float(v)
                    fb_spend[k] = round(fb_temp, 2)

                fb_projected_val = projected(client.fb_spend)
                fb_projected_per_day = fb_projected_val / last_day.day
                for index, val in enumerate(pdays):
                    fb_projected[val.strftime("%Y-%m-%d")] = round((fb_projected_per_day * index) + f.current_spend, 2)

                fb_budget_per_day = round(client.fb_budget / last_day.day, 2)
                for index, val in enumerate(bdays, start=1):
                    fb_budget[val.strftime("%Y-%m-%d")] = round(fb_budget_per_day * index, 2)

        else:
            fb_spend = {}
            fb_projected = {}
            fb_budget = {}

        new_client_cdata.aw_budget = aw_budget
        new_client_cdata.aw_spend = aw_spend
        new_client_cdata.aw_projected = aw_projected
        new_client_cdata.bing_budget = bing_budget
        new_client_cdata.bing_spend = bing_spend
        new_client_cdata.bing_projected = bing_projected
        new_client_cdata.fb_budget = fb_budget
        new_client_cdata.fb_spend = fb_spend
        new_client_cdata.fb_projected = fb_projected

        new_client_cdata.save()
        client.save()

        print('Updated current spend and chart data for client ' + client.client_name)

if __name__ == '__main__':
    main()