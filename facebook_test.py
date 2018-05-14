import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from facebook_dashboard.models import FacebookAccount
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adaccountuser import AdAccountUser
from datetime import date, timedelta

# from facebook_business.adobjects.business import Business
from facebook_business.adobjects.ad import Ad

now = date.today()
minDate = date.today().replace(day=1)
maxDate = now - timedelta(days=1)
# print(minDate)
# print(maxDate)

bloomworker='100025980313978'
my_app_id = '582921108716849'
business_id = '10154654586810511'
my_app_secret = '17bc991966f6895650068fe41bc87aa0'
ll_token = "EAAISKeWdZCTEBABaA5WtXSNP3vOGxEAFx2MBjKWGV6nfpOVxcMoHtTuqeyGx47rkDXJWErA4SPI1ikCHIKLOmorHpqHkNKxuEuSudMtjPdiLGV6MZArB4HRJPhDlpHmq53qrqarZBPMyClGOkhOMBGZBYmQUQXGX6pEFlHaO2gZDZD"

FacebookAdsApi.init(my_app_id, my_app_secret, ll_token)


accounts = []
# business = Business(fbid=business_id)

# allAdAccounts = business.get_owned_ad_accounts({AdAccount.Field.name})
# print(allAdAccounts[2]['id'])

# for i in range(len(allAdAccounts)):
#     print(allAdAccounts[i]['id'], allAdAccounts[i]['name'])

def get_accounts():
    me = AdAccountUser(fbid='me')

    for acc in me.get_ad_accounts():
        print(acc)
        if acc['id'] == 'act_220247200':
            continue
        else:
            account = {
                'id': acc['id']
            }
        accounts.append(account)
    sorted(accounts, key=lambda k: k['id'])
    # accounts = accounts.pop(1)
    # print(accounts)
    return accounts
def get_spend(accounts):
    for acc in accounts:
        my_account = AdAccount(acc['id'])
        fields = [
            'account_name',
            'account_id',
            'spend',
        ]
        params = {
            'level': 'account',
            'filtering': [],
            'breakdowns': [],
            'time_range': {'since':str(minDate),'until':str(maxDate)},
        }

        insights = my_account.get_insights(
            fields=fields,
            params=params,
        )

        print(insights)

        try:
            FacebookAccount.objects.get(account_id=insights[0]['account_id'])
            print('Matched in DB(' + str(insights[0]['account_id']) + ')')
        except IndexError:
            continue
        except:
            FacebookAccount.objects.create(account_name=insights[0]['account_name'],
                                                  account_id=insights[0]['account_id'],
                                                  current_spend=insights[0]['spend'])
            print('Added to DB - ' + str(insights[0]['account_id']) + ' - ' + insights[0]['account_name'])


def main():
    accounts = get_accounts()
    get_spend(accounts)

if __name__ == '__main__':
    main()