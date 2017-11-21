from googleads import adwords
import get_accounts

client = adwords.AdWordsClient.LoadFromStorage('../google_auth/googleads.yaml')
accounts = get_accounts.get_dependent_accounts()

def get_account_cost(client, accounts):

    cost_report = {
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
