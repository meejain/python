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
currentregPL = []
prefixListCIDR = []

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


def creation_of_PL(arg_region,arg_plcidr):
    session = boto3.Session(profile_name=arg_profile, region_name=arg_region)
    client = session.client('ec2')
    response = client.create_managed_prefix_list(
        PrefixListName='testPL_CM_Azure_Whitelisting',
        MaxEntries=60,
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


def updating_of_pl():
    print('Do you want to update Prefix Lists of any region ')
    ans = str(input(""))
    if ans == "yes":
        print('which region ')
        rgn = str(input(""))
        with open('test_file.json', 'r') as k:
            json_data1 = json.load(k)
            for v in json_data1[rgn]:
                currentregPL.append(v)
            if len(currentregPL) == noofPL:
                initial = 0
                final = 60
                for pl in currentregPL:
                    session1 = boto3.Session(profile_name=arg_profile, region_name=rgn)
                    client1 = session1.client('ec2')
                    response1 = client1.get_managed_prefix_list_entries(
                        PrefixListId=pl,
                    )
                    for i in response1['Entries']:
                        prefixListCIDR.append({"Cidr": i['Cidr']})
                    print (pl)
                    print (prefixListCIDR)
                    session2 = boto3.Session(profile_name=arg_profile, region_name=rgn)
                    client2 = session2.client('ec2')
                    response2 = client2.describe_managed_prefix_lists(
                        DryRun=False,
                        PrefixListIds=[pl]
                    )
                    prefixListVersion1 = response2['PrefixLists'][0]['Version']
                    session3 = boto3.Session(profile_name=arg_profile, region_name=rgn)
                    client3 = session3.client('ec2')
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
                    time.sleep(10)
                    print('Do you want to add the new entries ')
                    ans1 = str(input(""))
                    if ans1 == "yes":
                        session4 = boto3.Session(profile_name=arg_profile, region_name=rgn)
                        client4 = session4.client('ec2')
                        response4 = client4.modify_managed_prefix_list(
                            DryRun=False,
                            CurrentVersion=prefixListVersion1,
                            PrefixListId=pl,
                            AddEntries=serviceTagCIDR[initial:final]
                        )
                        prefixListVersion1 += 1
                        initial = initial + 60
                        final = final + 60





def main():
    initial = 0
    final = 60
    preparing_list_Azure_US_East()
    calculate_no_of_PL()
    print('Enter the Region ')
    REGION = str(input(""))
    for x in range(1, (noofPL+1)):
        plcidr=serviceTagCIDR[initial:final]
        creation_of_PL(REGION,plcidr)
        initial = initial + 60
        final = final + 60
    json_editing(prefix_list_ids,REGION)
    prefix_list_ids.clear()
    updating_of_pl()



main()


