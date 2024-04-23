import requests
import re
import json
import sys
import time


try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    sys.exit("Could not import 'boto3', please install this package.")
region_pl_list = []
serviceTagCIDR = []
arg_profile='bpbu19-stage'
prefix_list_ids = []
prefixListVersion = int()

def test():
    print("hey buddy")


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



def json_editing(prefix,reg):
    with open('test_file.json', 'r') as j:
        json_data = json.load(j)
        #print('Enter the Region ')
        #REGION = str(input(""))
        #for i in json_data[REGION]:
           # region_pl_list.append(i)
    #print (region_pl_list)
    j.close()
    #prefix=["p1","p2","p3"]
    json_data[reg]=prefix
    with open('test_file.json', 'w') as x:
        json.dump(json_data,x)


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


def creation_of_PL(arg_region,arg_plcidr,arg_x):
    session = boto3.Session(profile_name=arg_profile, region_name=arg_region)
    client = session.client('ec2')
    response = client.create_managed_prefix_list(
        PrefixListName=f'AMSBasic-PL_CM_Azure_Whitelisting{arg_x}',
        MaxEntries=60,
        TagSpecifications=[
            {
                'ResourceType': 'prefix-list',
                'Tags': [
                    {
                        'Key': 'CMDB_device_service',
                        'Value': 'Managed Services - AEM Basic - PrefixList'
                    },
                    {
                        'Key': 'Usage',
                        'Value': 'CloudManager Asset Perf Testing - MSFT US East Region - Allowlisting'
                    },
                    {
                        'Key': 'Owner',
                        'Value': 'meejain@adobe.com'
                    },
                ]
            },
        ],
        AddressFamily='IPv4',
    )
    pl_id=response['PrefixList']['PrefixListId']
    prefixListVersion = response['PrefixList']['Version']
    print(prefixListVersion)
    print(pl_id)
    prefix_list_ids.append(pl_id)
    print(arg_plcidr)
    response = client.modify_managed_prefix_list(
        DryRun=False,
        PrefixListId=pl_id,
        CurrentVersion=prefixListVersion,
        AddEntries=arg_plcidr
    )




def main():
    initial = 0
    final = 60
    preparing_list_Azure_US_East()
    calculate_no_of_PL()
    print('Enter the Region ')
    REGION = str(input(""))
    for x in range(1, 5):
        plcidr=serviceTagCIDR[initial:final]
        creation_of_PL(REGION,plcidr,x)
        initial = initial + 60
        final = final + 60
    json_editing(prefix_list_ids,REGION)
    prefix_list_ids.clear()



main()


