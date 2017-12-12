#################
# @author: StefanM
#################

import time
import gc
import logging
import datetime
import io
import csv
from googleads import adwords

logging.basicConfig(level=logging.INFO)


class AlertSystem(object):

    match_counter = 0
    campaigns = []
    adgroups = []
    keywords = []
    negatives = []
    adgroup_negatives = []
    positives = []
    blocked_examples = []
    adgroup_ads = []
    PAGE_SIZE = 7500

    def __init__(self, client, customerId):
        self.customerId = customerId
        self.client = client
        self.client.SetClientCustomerId(customerId)
        self.blocked = 0

    def getCampaigns(self):
        now = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
        offset = 0

        campaign_service = self.client.GetService('CampaignService', version='v201705')

        campaign_selector = {'fields': ['Id', 'Status','Name'],
                             'predicates': [
                                 {
                                     'field': 'Status',
                                     'operator': 'EQUALS',
                                     'values': 'ENABLED'
                                 },{
                                     'field': 'EndDate',
                                     'operator': 'GREATER_THAN',
                                     'values': now

                                 }],
                             'paging': {
                                 'startIndex': str(offset),
                                 'numberResults': str(self.PAGE_SIZE)
                             }}
        more_pages = True
        while more_pages:
            page = campaign_service.get(campaign_selector)
            time.sleep(0.5)
            if 'entries' in page and page['entries']:

                self.campaigns.extend(page['entries'])
                offset += self.PAGE_SIZE
                campaign_selector['paging']['startIndex'] = str(offset)

            more_pages = offset < int(page['totalNumEntries'])
        return self.campaigns


    def getAdgroups(self):
        offset = 0

        adgroup_service = self.client.GetService('AdGroupService', version='v201705')

        adgroup_selector =  {'fields': ['Id', 'AdGroupName','Status','CampaignId','CampaignName'],
                             'predicates': [
                                 {
                                     'field': 'Status',
                                     'operator': 'EQUALS',
                                     'values': 'ENABLED'
                                 },
                                 {
                                     'field': 'CampaignId',
                                     'operator': 'IN',
                                     'values': [str(campaign.id) for campaign in self.campaigns[:10000]]
                                 }
                             ],
                             'paging': {
                                 'startIndex': str(offset),
                                 'numberResults': str(self.PAGE_SIZE)
                             }}

        more_pages = True
        if self.campaigns:
            while more_pages:
                try:
                    if offset > 10000:
                        break
                    page = adgroup_service.get(adgroup_selector)
                    if 'entries' in page and page['entries']:
                        self.adgroups.extend(page['entries'])
                finally:
                    offset += self.PAGE_SIZE
                    adgroup_selector['paging']['startIndex'] = str(offset)
                    more_pages = offset < int(page['totalNumEntries'])

            return self.adgroups

    def getAds(self):
        offset = 0

        ad_service = self.client.GetService('AdGroupAdService', version='v201705')

        ad_selector =  {'fields':['Id', 'HeadlinePart1', 'PolicySummary', 'AdGroupName', 'AdGroupId'],
                        'predicates': [
                            {
                                'field': 'Status',
                                'operator': 'EQUALS',
                                'values': 'ENABLED'
                            },
                            {
                             'field': 'AdGroupId',
                             'operator': 'IN',
                             'values': [str(adgroup.id) for adgroup in self.adgroups[:100000]]
                            }
                            ],
                        'paging': {
                         'startIndex': str(offset),
                         'numberResults': str(self.PAGE_SIZE)
                         }}


        more_pages = True
        if self.adgroups:
            while more_pages:
                page = ad_service.get(ad_selector)
                if offset > 10000:
                    break
                if 'entries' in page and page['entries']:
                    self.adgroup_ads.extend(page['entries'])

                offset += self.PAGE_SIZE
                ad_selector['paging']['startIndex'] = str(offset)
                more_pages = offset < int(page['totalNumEntries'])
            return self.adgroup_ads

    def getKeywords(self):
        offset = 0
        adgroup_criterion_service = self.client.GetService('AdGroupCriterionService', version='v201705')
        adgroup_criterion_selector = {
                    'fields':['Id','KeywordText','KeywordMatchType','AdGroupId','Status'],
                    'predicates': [
                        {
                            'field': 'Status',
                            'operator': 'EQUALS',
                            'values': 'ENABLED'
                        },
                        {
                            'field': 'AdGroupId',
                            'operator': 'IN',
                            'values': [str(adgroup.id) for adgroup in self.adgroups[:100000]]
                        }],
                    'paging': {
                        'startIndex': str(offset),
                        'numberResults': str(self.PAGE_SIZE)
                    }}

        more_pages = True
        if self.adgroups:
            while more_pages:
                page = adgroup_criterion_service.get(adgroup_criterion_selector)

                if 'entries' in page and page['entries']:
                    self.keywords.extend(page['entries'])
                if offset > 10000:
                    break

                offset += self.PAGE_SIZE
                adgroup_criterion_selector['paging']['startIndex'] = str(offset)
                more_pages = offset < int(page['totalNumEntries'])

            return self.keywords

    def getPositiveKeywords(self):

        positive_keywords = {
            'reportName' : 'POSITIVE_KEYWORDS',
            'dateRangeType' : 'YESTERDAY',
            'reportType' : 'KEYWORDS_PERFORMANCE_REPORT',
            'downloadFormat' : 'CSV',
            'selector' : {
                'fields' : ['CampaignId', 'CampaignName', 'AdGroupId', 'Id', 'KeywordMatchType', 'Criteria'],
                'predicates' : [{
                        'field': 'CampaignStatus',
                        'operator': 'IN',
                        'values' : ['ENABLED']},
                    {
                        'field': 'AdGroupStatus',
                        'operator': 'IN',
                        'values': ['ENABLED']},
                    {
                        'field': 'Status',
                        'operator': 'IN',
                        'values': ['ENABLED']},
                    {
                        'field': 'IsNegative',
                        'operator': 'IN',
                        'values': ['false']
                    }],
                    }
                }

        service = self.client.GetReportDownloader(version='v201705')
        dataCampaignReport = service.DownloadReportAsString(positive_keywords,
                                                            use_raw_enum_values=True, skip_report_header=True,
                                                            skip_report_summary=True)
        # Data parsing
        try:
            dictData = StringIo.StringIo(dataCampaignReport)
        except:
            dictData = io.StringIO(dataCampaignReport)
        self.positives = list(csv.DictReader(dictData))
        return self.positives

    def getAdGroupNegatives(self):

        adgroup_negatives = {
            'reportName' : 'ADGROUP_NEGATIVES',
            'dateRangeType' : 'YESTERDAY',
            'reportType' : 'KEYWORDS_PERFORMANCE_REPORT',
            'downloadFormat' : 'CSV',
            'selector' : {
                'fields' : ['CampaignId', 'CampaignName', 'AdGroupId', 'AdGroupName', 'Id', 'KeywordMatchType', 'Criteria'],
                'predicates' : [{
                        'field': 'CampaignStatus',
                        'operator': 'IN',
                        'values' : ['ENABLED']},
                    {
                        'field': 'AdGroupStatus',
                        'operator': 'IN',
                        'values': ['ENABLED']},
                    {
                        'field': 'Status',
                        'operator': 'IN',
                        'values': ['ENABLED']},
                    {
                        'field': 'IsNegative',
                        'operator': 'IN',
                        'values': ['true']
                    }],
                    }
                }

        service = self.client.GetReportDownloader(version='v201705')
        dataCampaignReport = service.DownloadReportAsString(adgroup_negatives,
                                                            use_raw_enum_values=True, skip_report_header=True,
                                                            skip_report_summary=True)
        # Data parsing
        try:
            dictData = StringIo.StringIo(dataCampaignReport)
        except:
            dictData = io.StringIO(dataCampaignReport)
        self.adgroup_negatives = list(csv.DictReader(dictData))
        return self.adgroup_negatives

    def getNegativeKeywords(self):

        negative_keywords = {
            'reportName' : 'NEGATIVE_KEYWORDS',
            'dateRangeType' : 'YESTERDAY',
            'reportType' : 'CAMPAIGN_NEGATIVE_KEYWORDS_PERFORMANCE_REPORT',
            'downloadFormat' : 'CSV',
            'selector' : {
                'fields' : ['CampaignId', 'Id', 'KeywordMatchType', 'Criteria']
                    }
                }

        service = self.client.GetReportDownloader(version='v201710')
        dataCampaignReport = service.DownloadReportAsString(negative_keywords,
                            use_raw_enum_values=True, skip_report_header=True,
                            skip_report_summary=True)

        # Data parsing
        try:
            dictData = StringIo.StringIo(dataCampaignReport)
        except:
            dictData = io.StringIO(dataCampaignReport)
        self.negatives = list(csv.DictReader(dictData))
        return self.negatives

    def add_blocked(self, keyword):
        # if self.blocked < 250:
        self.blocked_examples.append(keyword)
            # self.blocked += 1

    def compareKeywords(self, negatives, positive):

        for negative in negatives:
            match_type = negative['Match type'].lower()
            negative_text = negative['Negative keyword'].lower()
            positive_text = positive['Keyword'].lower()

            match = False

            # If the negative keyword is more strict than the positive one, it cannot match
            positive_match_type = positive['Match type'].lower()
            if positive_match_type == 'broad' and match_type != 'broad':
                continue
            if positive_match_type == 'phrase' and match_type == 'exact':
                continue

            # Exact matching with negative keywords triggers only when the full text of
            # the keywords is exactly the same.
            if match_type == 'exact':
                match = (negative_text == positive_text)
                # print(str(match) + ' - [EXACT]')

            # Phrase matching with negative keywords triggers when the negative phrase
            # is present in the target, completely unmodified.
            if match_type == 'phrase':

                positive_tokens = positive_text.split(' ')
                match = (negative_text in positive_tokens)


                # match = (negative_text in positive_text)
                # if negative_text in positive_text:
                #     match = True

                # negative_tokens = negative_text.split(' ')
                # positive_tokens = positive_text.split(' ')
                # print('Positives: ',positive_tokens)
                # print('Negatives: ', negative_tokens)
                # for positive_index, positive_token in enumerate(positive_tokens):
                #     if positive_token == negative_tokens[0]:
                #         canditate_match = True
                #         for index, token in enumerate(negative_tokens[1::]):
                #             print('Len positive tokens: ', len(positive_tokens))
                #             print('Len negative tokens: ', len(negative_tokens))
                #             print('Index: ', index)
                #             print('Positive index: ', positive_index)
                #             if token != positive_tokens[positive_index+index+1]:
                #                 canditate_match = False
                #                 break
                #             print('Candidate match: ', canditate_match)
                #         match = canditate_match
                # print(str(match) + ' - [PHRASE]')
                # if match:
                #     print('Match: ' + str(match))
                #     print(negative_text, positive_text)

            # Broad matching with negative keywords triggers when all of the words are
            # present and exactly the same.
            if match_type == 'broad':
                negative_tokens = negative_text.split(' ')
                positive_tokens = positive_text.split(' ')

                canditate_match = True

                for token in negative_tokens:
                    if token not in positive_tokens:
                        canditate_match = False
                        break

                match = canditate_match
                # print(str(match) + ' - [BROAD]')
                # print(positive_text)

            if match:
                conflict = {}
                conflict[negative_text] = positive
                self.add_blocked(conflict)


    def buildAlerts(self):
        self.getCampaigns()
        self.getAdgroups()
        self.getAds()
        # self.getKeywords()

    def duplicateCheck(self):
        valid_keywords = [keyword for keyword in self.keywords if hasattr(keyword.criterion, 'text') and hasattr(keyword.criterion, 'matchType')]
        dupes = []
        for adgroup in self.adgroups:
            adgroup_keywords = [keyword for keyword in valid_keywords if keyword.adGroupId == adgroup.id]
            duplicates = [keyword for i, keyword in enumerate(adgroup_keywords) if (keyword.criterion.text, keyword.criterion.matchType) in \
                            [(keyword1.criterion.text, keyword1.criterion.matchType) for keyword1 in adgroup_keywords[:i]]]
            dupes.extend(duplicates)

            # keywords_text = [keyword.criterion.text for keyword in adgroup_keywords]
            # dup = [keyword for keyword, count in collections.Counter(keywords_text).items() if count > 1]
            # data_dup = [keyword for keyword in adgroup_keywords if keyword.criterion.text in dup]
            # dupes.extend(data_dup)
        return dupes

    def disapprovedCheck(self):

        return [ad for ad in self.adgroup_ads if ad.policySummary.combinedApprovalStatus == "DISAPPROVED"]

    def emptyAdsCheck(self):
        return [adgroup for adgroup in self.adgroups if str(adgroup.id) not in [str(ad.adGroupId) for ad in self.adgroup_ads]]

    def emptyAdGroup(self):
        return [campaign for campaign in self.campaigns if str(campaign.id) not in [str(adgroup.campaignId) for adgroup in self.adgroups]]

    def cleanMemory(self):
        del self.campaigns[:]
        del self.adgroups[:]
        del self.adgroup_ads[:]
        del self.adgroups[:]
        del self.blocked_examples[:]
        del self.positives[:]
        del self.negatives[:]
        del self.adgroup_negatives[:]
        gc.collect()

def main():
    client = adwords.AdWordsClient.LoadFromStorage('../google_auth/googleads.yaml')
    a = AlertSystem(client, '6188738871')


if __name__ == '__main__':
    main()