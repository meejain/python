import requests
import re
import json
import sys
import time
import os
import boto3


serviceTagCIDR = []
prefixListVersion = int()
currentregPL = []
prefixListCIDR = []


def preparing_list_Azure_US_East():
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


def calculate_no_of_PL():
    global noofPL
    global size
    size = len(serviceTagCIDR)
    rem = size % 60
    quot = size // 60
    if rem > 0:
        noofPL = quot + 1
    else:
        noofPL = quot
    print('The No. of Prefix Lists that should be there are %s.' % (noofPL))


def updating_of_pl():
    rgn = os.environ['AWS_REGION']
    print (rgn)
    with open('amsbasic_prefixlist_CM.json', 'r') as k:
        json_data1 = json.load(k)
        for v in json_data1[rgn]:
            currentregPL.append(v)
        if len(currentregPL) == noofPL:
            initial = 0
            final = 60
            for pl in currentregPL:
                client1 = boto3.client('ec2')
                response1 = client1.get_managed_prefix_list_entries(
                    PrefixListId=pl,
                )
                for i in response1['Entries']:
                    prefixListCIDR.append({"Cidr": i['Cidr']})
                print(pl)
                print(prefixListCIDR)
                client2 = boto3.client('ec2')
                response2 = client2.describe_managed_prefix_lists(
                    DryRun=False,
                    PrefixListIds=[pl]
                )
                prefixListVersion1 = response2['PrefixLists'][0]['Version']
                print(prefixListVersion1)
                client3 = boto3.client('ec2')
                response3 = client3.modify_managed_prefix_list(
                    DryRun=False,
                    CurrentVersion=prefixListVersion1,
                    PrefixListId=pl,
                    RemoveEntries=prefixListCIDR
                )
                prefixListCIDR.clear()
                prefixListVersion1 += 1
                print("Removal in process")
                print(response3)
                time.sleep(15)
                # print('Do you want to add the new entries ')
                # ans1 = str(input(""))
                # if ans1 == "y":
                client4 = boto3.client('ec2')
                response4 = client4.modify_managed_prefix_list(
                    DryRun=False,
                    CurrentVersion=prefixListVersion1,
                    PrefixListId=pl,
                    AddEntries=serviceTagCIDR[initial:final]
                )
                prefixListVersion1 += 1
                initial = initial + 60
                final = final + 60



def lambda_handler(event, context):
    preparing_list_Azure_US_East()
    calculate_no_of_PL()
    updating_of_pl()







