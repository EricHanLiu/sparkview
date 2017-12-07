from googleads import adwords
from operator import itemgetter
import logging
import sys
import io
import csv
logging.basicConfig(level=logging.INFO)



#################### VARIABLES #####################

PAGE_SIZE = 2000
PATH_TO_VALID_YAML = '../../atcore/googleAuth/googleads.yaml'
CHECK_VALID_CAMPAIGNS_FLAG = False
NUMBER_OF_FAILURE_RETRIES = 5

####################################################

#Reduced API Calls to NumberOfAccountsWithinMCC/PAGE_SIZE [In our case there are at the moment about 350 accounts and such we have here just one API call]
#Use ManagedCustomerService in order to get all accounts within MCC
#Use details inside ManagedCustomerPage entries links and canManageAccounts selector field in order to create account hierarchy
#Use adwordsAPI approach with paging and a limit to 500 results per page
#Can select wether to check for valid campaigns within account or not, choosing to check for valid campaigns will make the script take longer


validCampaignDictionary = {}

def getRawStructure(client):

    #client.SetClientCustomerId('2917515327')
    #client.SetClientCustomerId('4105551527')
    #client.SetClientCustomerId('4941667276')
    #client.SetClientCustomerId('5275180975')
    #client.SetClientCustomerId('5931344867')
    #client.SetClientCustomerId('2266301477')
    #client.SetClientCustomerId('8980957531')
    #client.SetClientCustomerId('9820878427')


    managed_customer_service = client.GetService('ManagedCustomerService', version='v201705')
    offset = 0

    selector = {
        'fields': ['CustomerId', 'Name', 'CanManageClients'],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        }
    }

    rawStructureDictionary = {}
    entries_list = []
    links_list = []
    more_pages = True

    while more_pages:
        page = managed_customer_service.get(selector)
        if 'entries' in page and page['entries']:
            entries_list.extend(page['entries'])
        if 'links' in page:
            links_list.extend(page['links'])


        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])

    rawStructureDictionary['ENTRIES'] = entries_list
    rawStructureDictionary['LINKS'] = links_list

    return rawStructureDictionary

def buildAccountTreeDictionary(rawStructure, checkValidCampaignsFlag):

    mainAccountDetailDictionary = {}
    mainAccountList = []
    dependentAccountDictionary = {}

    accountTreeDictionary = {}
    accountTreeDetailDictionary = {}
    accountTreeList = []

    for rawDetail in rawStructure['ENTRIES']:
        if(rawDetail['canManageClients']):
            mainAccountDetailDictionary['mainAccountName'] = rawDetail['name']
            mainAccountDetailDictionary['mainAccountId'] = rawDetail['customerId']
            mainAccountList.append(mainAccountDetailDictionary)
            mainAccountDetailDictionary = {}
        else:
            dependentAccountDictionary[rawDetail['customerId']] = rawDetail['name']

    for mainAccount in mainAccountList:

        mainAccountId = mainAccount['mainAccountId']

        for rawDetail in rawStructure['LINKS']:

            if(rawDetail['managerCustomerId'] == mainAccountId):
                if (rawDetail['clientCustomerId'] in map(itemgetter('mainAccountId'), mainAccountList)):
                    continue

                dependentAccountId = rawDetail['clientCustomerId']

                if(checkValidCampaignsFlag):
                    if not (getValidCampaignLength(dependentAccountId,client) > 0):
                         continue

                accountTreeDetailDictionary['mainAccountName'] = mainAccount['mainAccountName']
                accountTreeDetailDictionary['dependentAccountId'] = dependentAccountId
                accountTreeDetailDictionary['dependentAccountName'] = dependentAccountDictionary.get(dependentAccountId)
                accountTreeList.append(accountTreeDetailDictionary)
                accountTreeDetailDictionary = {}

        accountTreeDictionary[mainAccount['mainAccountId']] = accountTreeList
        accountTreeList = []

    return accountTreeDictionary

def getValidCampaignLength(account,client):

    excededNumberOfTriesCounter = 0
    campaignServiceEntries = []

    campaign_offset = 0

    client.SetClientCustomerId(account)
    campaign_service = client.GetService('CampaignService', version='v201705')


    campaign_selector = {'fields': ['Id', 'Status'],
                                 'predicates': [
                                     {
                                         'field': 'Status',
                                         'operator': 'EQUALS',
                                         'values': 'ENABLED'
                                     }],
                                 'paging': {
                                     'startIndex': str(campaign_offset),
                                     'numberResults': str(PAGE_SIZE)
                                 }}


    more_campaign_group_pages = True
    retry = True

    while more_campaign_group_pages:
        while retry:
            try:
                page = campaign_service.get(campaign_selector)
                retry = False
            except:
                retry = True
                if(excededNumberOfTriesCounter > NUMBER_OF_FAILURE_RETRIES):
                    break
                excededNumberOfTriesCounter += 1
                pass

        if 'entries' in page and page['entries']:
            campaignServiceEntries.extend(page['entries'])
            campaign_offset += PAGE_SIZE
            campaign_selector['paging']['startIndex'] = str(campaign_offset)
            more_campaign_group_pages = campaign_offset < int(page['totalNumEntries'])
        else:
            return 0

        for campaignEntry in campaignServiceEntries:
            validCampaignDictionary[campaignEntry['id']] = campaignEntry['status']
    return len(campaignServiceEntries)

def downloadReportWithRetryingOnFailure(method):

    retryFlag = True
    retryCounter = 0

    downloadedReportAsString = ""

    while retryFlag:
        try:
            downloadedReportAsString = method()
            retryFlag = False

        except:
            retryCounter+=1

            if(retryCounter > 5):
                return downloadedReportAsString
            print "Trying again. No. of tries:" + str(retryCounter)
    return downloadedReportAsString

def returnAccountsAverageSpend(accountTreeDictionary,client):

    report14Days = {
            'reportName': 'COST_REPORT',
            'dateRangeType': 'THIS_MONTH',
            'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': ['Cost']
            }
    }

    accountTreeWithEstimates = {}

    for mainAccount,dependentAccountsList in accountTreeDictionary.items():

        accountList = []
        #cost = 0
        totalEstimatedCost = 0
        for dependentAccount in dependentAccountsList:
            estimatedCost = 0
            mainAccountName = dependentAccount['mainAccountName']
            client.SetClientCustomerId(dependentAccount['dependentAccountId'])
            service = client.GetReportDownloader(version='v201705')

            data14Days = downloadReportWithRetryingOnFailure(lambda: service.DownloadReportAsString(report14Days,
                            skip_report_header=True, skip_report_summary=True, use_raw_enum_values=True))

            if len(data14Days) < 1:
                continue

            try:
                data = String.Io.String.Io(data14Days)
            except:
                data = io.StringIO(data14Days)

            data = list(csv.DictReader(data))

            if(len(data) == 0):

                accountEstimateDict = {}
                accountEstimateDict["accountId"] = dependentAccount['dependentAccountId']
                accountEstimateDict["accountName"] = dependentAccount['dependentAccountName']
                accountEstimateDict["estimatedCost"] = 0
                accountList.append(accountEstimateDict)

            else:

                accountEstimateDict = {}
                estimatedCost+=float(data[0]['Cost'])/1000000

                totalEstimatedCost += float(estimatedCost)
                #print totalEstimatedCost
                accountEstimateDict["accountId"] = dependentAccount['dependentAccountId']
                accountEstimateDict["accountName"] = dependentAccount['dependentAccountName']
                accountEstimateDict["estimatedCost"] = totalEstimatedCost
                accountList.append(accountEstimateDict)
                totalEstimatedCost = 0


        keyDictionary = {}
        keyDictionary["accountDetails"] = accountList
        keyDictionary["mainAccountName"] = mainAccountName
        accountTreeWithEstimates[mainAccount] = keyDictionary

    return accountTreeWithEstimates

def main(client):

     print "Starting Logic ... "
     print "Building account tree..."
     accountTree = buildAccountTreeDictionary(getRawStructure(client), CHECK_VALID_CAMPAIGNS_FLAG)
     print accountTree
     print "Processed account tree structure"
     print "Calculating cost per account, please wait..."
     averageSpend = returnAccountsAverageSpend(accountTree, client)
     return averageSpend


if __name__ == '__main__':
  # Initialize client object.
  client = adwords.AdWordsClient.LoadFromStorage(PATH_TO_VALID_YAML)
  print main(client)
