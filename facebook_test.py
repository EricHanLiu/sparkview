from facebookads.api import FacebookAdsApi
from facebookads.adobjects.adaccountuser import AdAccountUser
from facebookads.adobjects.campaign import Campaign

my_app_id = '720167181523779'
my_app_secret = '63df1a8d9448f2ea766c644c059e7b7a'
my_access_token = 'EAAKOZCP0Im0MBAHaSTqvVgBepTJD84YvQoZAdyHmKIImHSF1J6i4BrAMH8ZB77DpBiBH7eFdZAchCVqlujcjvw3ZBdJe99i5BReNJZAYN9OsUh3HWhFn445tZCqqfZCjrj3NUgPjadfwhoZAv8FBSuKdZBRZBW6i7dN4pRzzzKLAw0IWQZDZD'

FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)

me = AdAccountUser(fbid='me')
my_account = me.get_ad_account()

for campaign in my_account.get_campaigns(fields=[Campaign.Field.name]):
    for stat in campaign.get_insights(fields=[
        'impressions',
        'clicks',
        'spend',
        'unique_clicks',
        'actions',]):
        print(campaign[campaign.Field.name])
        # for statfield in stat:
        #     print("\t%s:\t\t%s" % (statfield, stat[statfield]))