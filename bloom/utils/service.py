from bingads.service_client import ServiceClient
from bloom.settings import BING_API_VERSION, ENVIRONMENT
from bing_dashboard import auth
from bloom import celery_app

class Service(object):

    def __init__(self):

        authorization = auth.BingAuth().get_auth()
        self.campaign_service = ServiceClient(
            "CampaignManagementService",
            version=BING_API_VERSION,
            authorization_data=authorization,
            environment=ENVIRONMENT
        )

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)

        if not callable(attr):
            return attr

        def set_account_id_before_call(*args, **kwargs):
            account_id = kwargs.get("account_id", None)
            if not account_id and name.startswith("get"):
                raise Exception("Account id is missing")
            self.campaign_service.authorization_data.account_id = account_id
            return attr(*args, **kwargs)

        return set_account_id_before_call

    def suds_object_to_dict(self, suds_object):
        item = dict(suds_object)
        keys = list(item.keys())
        for k in keys:
            item[k] = str(item[k])

        return item




class BingService(Service):

    def __init__(self):
        super().__init__()

    def get_campaigns(self, account_id=None):
        response = self.campaign_service.GetCampaignsByAccountId(
            AccountId=account_id, CampaignType=["SearchAndContent"]
        )

        if response and hasattr(response, 'Campaign'):
            response = response.Campaign
        else:
            response = []

        return response

    def get_ads_by_status(self, account_id=None, adgroup_id=None, status="Disapproved"):
        ad_types = [
            "Text",
            "Product",
            "ResponsiveAd",
            "Image",
            "ExpandedText",
            "DynamicSearch",
            "AppInstall"
        ]
        arr_adtypes = self.campaign_service.factory.create("ArrayOfAdType")
        arr_adtypes.AdType.extend(ad_types)

        ads = self.campaign_service.GetAdsByEditorialStatus(
            AdGroupId=adgroup_id, AdTypes=arr_adtypes, EditorialStatus=status
        )
        if ads and hasattr(ads, 'Ad'):
            ads = ads.Ad
        else:
            ads = []

        return ads
