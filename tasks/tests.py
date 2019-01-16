from django.test import TestCase, Client
from bloom.utils.reporting import Reporting


class AdTasksTestCase(TestCase):

    def test_get_change_no(self):
        """
        Check all of the regular user views
        """
        change_data = {
            'changedCampaigns': [
                {
                    'campaignId': 1620360235,
                    'campaignChangeStatus': 'FIELDS_UNCHANGED',
                    'changedAdGroups': [
                        {
                            'adGroupId': 63200341802,
                            'adGroupChangeStatus': 'FIELDS_UNCHANGED',
                            'changedAds': [
                                123456,
                                84705241,
                                84705242,
                                84705243
                            ],
                            'changedCriteria': [],
                            'removedCriteria': [],
                            'changedFeeds': [
                                84705249
                            ],
                            'removedFeeds': [],
                            'changedAdGroupBidModifierCriteria': [],
                            'removedAdGroupBidModifierCriteria': []
                        },
                        {
                            'adGroupId': 63200341842,
                            'adGroupChangeStatus': 'FIELDS_UNCHANGED',
                            'changedAds': [],
                            'changedCriteria': [],
                            'removedCriteria': [],
                            'changedFeeds': [
                                84705248
                            ],
                            'removedFeeds': [],
                            'changedAdGroupBidModifierCriteria': [],
                            'removedAdGroupBidModifierCriteria': []
                        },
                        {
                            'adGroupId': 63200341882,
                            'adGroupChangeStatus': 'FIELDS_UNCHANGED',
                            'changedAds': [],
                            'changedCriteria': [],
                            'removedCriteria': [],
                            'changedFeeds': [
                                84705247
                            ],
                            'removedFeeds': [],
                            'changedAdGroupBidModifierCriteria': [],
                            'removedAdGroupBidModifierCriteria': []
                        }
                    ],
                    'addedCampaignCriteria': [],
                    'removedCampaignCriteria': [],
                    'changedFeeds': [],
                    'removedFeeds': []
                },
            ],
            'changedFeeds': [],
            'lastChangeTimestamp': '20190114 102549 PST8PDT'
        }

        change_number = Reporting.get_change_no(change_data)
        print(change_number)
        self.assertEqual(3, change_number)
