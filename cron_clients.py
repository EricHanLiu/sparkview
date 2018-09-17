import os
import django
import collections
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
import unicodedata
from budget.models import Client, ClientCData
from calendar import monthrange
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', str(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta

def projected(spend, yspend):

    today = datetime.today() - relativedelta(days=1)
    lastday_month = monthrange(today.year, today.month)
    remaining = lastday_month[1] - today.day

    # projected value
    rval = spend + (yspend * remaining)

    return round(rval ,2)

def main():

    today = date.today() - relativedelta(days=1)
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

    remaining = last_day.day - today.day

    pdays = []
    bdays = []

    for result in perdelta(today, last_day, timedelta(days=1)):
        pdays.append(result)

    for result in perdelta(first_day, last_day, timedelta(days=1)):
        bdays.append(result)



    clients = Client.objects.all()

    for client in clients:

        aw_s_final, aw_p_final, aw_b_final = {}, {}, {}
        bing_b_final, bing_p_final, bing_s_final = {}, {}, {}
        fb_b_final, fb_p_final, fb_s_final = {}, {}, {}

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

                aw_budget, aw_spend, aw_projected = {}, {}, {}

                account_name = a.dependent_account_name
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
                aw_s_final['A - ' + remove_accents(account_name) + ' Spend'] = aw_spend

                aw_projected_val = projected(a.current_spend, a.yesterday_spend)
                aw_projected_per_day = (aw_projected_val - a.current_spend) / remaining
                for index, val in enumerate(pdays):
                    aw_projected[val.strftime("%Y-%m-%d")] = round((aw_projected_per_day * index) + a.current_spend, 2)
                aw_p_final['A - ' + remove_accents(a.dependent_account_name) + ' Projected'] = aw_projected

                aw_budget_per_day = round(a.desired_spend / last_day.day, 2)
                for index, val in enumerate(bdays, start=1):
                    aw_budget[val.strftime("%Y-%m-%d")] = round(aw_budget_per_day * index, 2)
                aw_b_final['A - ' + remove_accents(a.dependent_account_name) + ' Budget'] = aw_budget
        else:
            aw_s_final = {}
            aw_b_final = {}
            aw_p_final = {}

        bing = client.bing.all()
        if len(bing) > 0:
            for b in bing:

                bing_budget, bing_spend, bing_projected = {}, {}, {}

                client.budget += b.desired_spend
                client.current_spend += b.current_spend
                client.bing_spend += b.current_spend
                client.yesterday_spend += b.yesterday_spend
                client.bing_budget += b.desired_spend

                for k, v in sorted(b.segmented_spend.items()):
                    b_temp = b_temp + float(v['spend'])
                    bing_spend[v['gregoriandate']] = round(b_temp, 2)
                bing_s_final['B - ' + remove_accents(b.account_name) + ' Spend'] = bing_spend

                bing_projected_val = projected(b.current_spend, b.yesterday_spend)
                bing_projected_per_day = (bing_projected_val - b.current_spend) / remaining
                for index, val in enumerate(pdays):
                    bing_projected[val.strftime("%Y-%m-%d")] = round((bing_projected_per_day * index) + b.current_spend, 2)
                bing_p_final['B - ' + remove_accents(b.account_name) + ' Projected'] = bing_projected

                bing_budget_per_day = round(b.desired_spend / last_day.day, 2)
                for index, val in enumerate(bdays, start=1):
                    bing_budget[val.strftime("%Y-%m-%d")] = round(bing_budget_per_day * index, 2)
                bing_b_final['B - ' + remove_accents(b.account_name) + ' Budget'] = bing_budget
        else:
            bing_s_final = {}
            bing_p_final = {}
            bing_b_final = {}


        facebook = client.facebook.all()
        if len(facebook) > 0:
            for f in facebook:

                fb_budget, fb_spend, fb_projected = {}, {}, {}

                client.budget += f.desired_spend
                client.current_spend += f.current_spend
                client.fb_spend += f.current_spend
                client.yesterday_spend += f.yesterday_spend
                client.fb_budget += f.desired_spend

                for k, v in sorted(f.segmented_spend.items()):
                    fb_temp = fb_temp + float(v)
                    fb_spend[k] = round(fb_temp, 2)
                fb_s_final['F - ' + remove_accents(f.account_name) + ' Spend'] = fb_spend

                fb_projected_val = projected(f.current_spend, f.yesterday_spend)
                fb_projected_per_day = (fb_projected_val - f.current_spend) / remaining
                for index, val in enumerate(pdays):
                    fb_projected[val.strftime("%Y-%m-%d")] = round((fb_projected_per_day * index) + f.current_spend, 2)
                fb_p_final['F - ' + remove_accents(f.account_name) + ' Projected'] = fb_projected

                fb_budget_per_day = round(f.desired_spend / last_day.day, 2)
                for index, val in enumerate(bdays, start=1):
                    fb_budget[val.strftime("%Y-%m-%d")] = round(fb_budget_per_day * index, 2)
                fb_b_final['F - ' + remove_accents(f.account_name) + ' Budget'] = fb_budget

        else:
            fb_s_final = {}
            fb_p_final = {}
            fb_b_final = {}

        new_client_cdata.aw_budget = aw_b_final
        new_client_cdata.aw_spend = aw_s_final
        new_client_cdata.aw_projected = aw_p_final
        new_client_cdata.bing_budget = bing_b_final
        new_client_cdata.bing_spend = bing_s_final
        new_client_cdata.bing_projected = bing_p_final
        new_client_cdata.fb_budget = fb_b_final
        new_client_cdata.fb_spend = fb_s_final
        new_client_cdata.fb_projected = fb_p_final

        new_client_cdata.save()
        client.save()

        # print('Updated current spend and chart data for client ' + client.client_name)

if __name__ == '__main__':
    main()