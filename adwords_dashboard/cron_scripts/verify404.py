from googleads import adwords
from bloom import settings
from .check_404 import Check404
import sys
import gc
import io


def checkURLS(detailList):
    checker = Check404(detailList)
    results = checker.get_results()
    badUrls = []
    for result in results:
        if result and result['code'] > 300:
            if result['code'] != 403:
                badUrls.append(result)
    gc.collect()
    return badUrls

def getData(client, account, add):
    """
    Function to retrieve URLS from adwords, and store them in DB
    @param: AdWordsClient
    @param: AdWords AccountId
    @param: Function

    """
    detailList = []

    CAMPAIGN_ID_REPORT_INDEX = 0
    CAMPAIGN_NAME_REPORT_INDEX = 1
    AD_GROUP_ID_REPORT_INDEX = 3
    AD_GROUP_NAME_REPORT_INDEX = 2
    HEADLINE_REPORT_INDEX = 5
    FINAL_URL_REPORT_INDEX = 4

    client.SetClientCustomerId(account)
    service = client.GetReportDownloader(version=settings.API_VERSION)

    report = {
        'reportName': 'COST_REPORT',
        'dateRangeType': 'ALL_TIME',
        'reportType': 'AD_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['CampaignId', 'CampaignName', 'AdGroupName', 'AdGroupId', 'CreativeFinalUrls',
                       'HeadlinePart1'],
            'predicates': [{
                'field': 'CampaignStatus',
                'operator': 'IN',
                'values': ['ENABLED']
                }, {
                'field': 'AdGroupStatus',
                'operator': 'IN',
                'values': ['ENABLED']
                }, {
                'field': 'Status',
                'operator': 'IN',
                'values': ['ENABLED']
                }]
        }
    }
    CHUNK_SIZE = 1024 * 1024
    report_data = io.StringIO()
    stream_data = service.DownloadReportAsStream(
      report, skip_report_header=True, skip_column_header=True,
      skip_report_summary=True, include_zero_impressions=True)

    try:
        while True:
            chunk = stream_data.read(CHUNK_SIZE)
            if not chunk:
                break
            report_data.write(chunk.decode() if sys.version_info[0] == 3
                            and getattr(report_data, 'mode', 'w') == 'w' else chunk)

            data = report_data.getvalue()
            keyWordReportArray = data.splitlines()
            keyWordReportArray.pop(0)
            keyWordReportArray = keyWordReportArray[:-1]
            detailList = []
            for row in keyWordReportArray:
                rowArray = row.split(",")
                adDetailDictionary = {}
                adDetailDictionary['CampaignId'] = rowArray[CAMPAIGN_ID_REPORT_INDEX]
                adDetailDictionary['CampaignName'] = rowArray[CAMPAIGN_NAME_REPORT_INDEX]
                adDetailDictionary['AdGroupId'] = rowArray[AD_GROUP_ID_REPORT_INDEX]
                adDetailDictionary['AdGroupName'] = rowArray[AD_GROUP_NAME_REPORT_INDEX]
                adDetailDictionary['HeadLine'] = rowArray[HEADLINE_REPORT_INDEX]
                adDetailDictionary['Link'] = rowArray[FINAL_URL_REPORT_INDEX].replace("\"", "").replace("[", "").replace("]", "").split(",")[0]
                if (str(rowArray[FINAL_URL_REPORT_INDEX]).strip() == "--"):
                    adDetailDictionary = {}
                    continue

                detailList.append(adDetailDictionary)
            badUrls = checkURLS(detailList)
            add(badUrls, client.client_customer_id.replace('-',''))
            print('added urls')
    # except ConnectionResetError as e:
    #     print(e)
    #     pass

    finally:
        report_data.close()
        stream_data.close()

    return detailList
