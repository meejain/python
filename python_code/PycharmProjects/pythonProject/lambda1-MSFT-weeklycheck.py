import requests
import re
import json
import sys
import time
from datetime import date
import boto3

serviceTagCIDR = []


def preparing_list_Azure_US_East():
    global today
    SERVICE_TAGS_URL = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'
    SERVICE_TAG = 'AzureCloud.eastus'
    with requests.get(SERVICE_TAGS_URL) as response:
        if response.status_code == 200:
            with requests.get(re.search('https://download.*?\.json', response.text).group()) as servicetagjson:
                if servicetagjson.status_code == 200:
                    data = json.loads(servicetagjson.text)
                    for i in data['values']:
                        if SERVICE_TAG.lower() == i['name'].lower():
                            for address in i['properties']['addressPrefixes']:
                                if not "::" in address:
                                    serviceTagCIDR.append({"Cidr": address})
                else:
                    print('An error occurred while attempting to retrieve json data from Microsoft.')
        else:
            print('An error occurred while attempting to retrieve data from Microsoft.')
    print(serviceTagCIDR)
    print(len(serviceTagCIDR))
    today = date.today()
    print(today)
    f1 = open(f'/tmp/{today}.json', 'w')
    f1.write(json.dumps(serviceTagCIDR))
    f1.close()


def sorting(item):
    if isinstance(item, dict):
        return sorted((key, sorting(values)) for key, values in item.items())
    if isinstance(item, list):
        return sorted(sorting(x) for x in item)
    else:
        return item


def comparejson():
    old_file = 'Prior-Week-MSFT-Azure-USEast-IPs.json'
    with open(f'./tmp/{old_file}', 'r') as x:
        json_data = json.load(x)
    with open(f'/tmp/{today}.json', 'r') as y:
        json_data1 = json.load(y)
    result = sorting(json_data) == sorting(json_data1)
    print(result)
    if result == False:
        a_file = open(f'/tmp/{today}.json', "r")
        a_json = json.load(a_file)
        pretty_json = json.dumps(a_json)
        a_file.close()
        print(pretty_json)
        client = boto3.client('sns')
        response = client.publish(
            TopicArn='arn:aws:sns:us-east-1:206073786279:MSFT_Weekly_Azure_USEAST_IP_Check',
            Message='MSFT US East Region IPs have changed this week. Please go ahead & update all the Prefix Lists allotted for Allow Listing Cloud Manager Asset Perf Test for BPBU17 & 18',
            Subject='MSFT US East Region IP change Notification - Cloud Manager Asset Performance Test'
        )


def lambda_handler(event, context):
    preparing_list_Azure_US_East()
    comparejson()

