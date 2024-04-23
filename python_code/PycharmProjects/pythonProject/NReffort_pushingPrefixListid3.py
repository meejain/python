import requests
import re
import json
import sys
import time
import collections

NR_SG_Entries = []
prefix_list_ids = []
currentregPL = []
arg_profile='bpbu19-stage'
prefixListCIDR = []


try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    sys.exit("Could not import 'boto3', please install this package.")



def preparing_sample_json():
 list1=["No Prefix List allotted"]
 NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
 with requests.get(NR_SYN_URL) as response:
   if response.status_code == 200:
        data = json.loads(response.text)
        print("The original dictionary is : " + str(data))
        NRregions=list(data.keys())
        with open("sample.json", "w") as outfile:
            json.dump(data, outfile)
        with open('sample.json', 'r') as j:
            json_data = json.load(j)
            for a in NRregions:
                json_data[a]=list1
                with open('sample.json', 'w') as x:
                    json.dump(json_data, x)

def Region_Check():
    NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
    with requests.get(NR_SYN_URL) as response:
        if response.status_code == 200:
            data = json.loads(response.text)
            NRregions = list(data.keys())
            with open(f'{AWS_REGION}_NR_PL.json', 'r') as j:
                json_data = json.load(j)
                localNRregions = list(json_data.keys())
                print (localNRregions)
                print (NRregions)
                if (collections.Counter(NRregions) != collections.Counter(localNRregions)):
                    print("Use the AWS SNS to email that NR Regions have changed - removed / added")
                    list_difference = [item for item in NRregions if item not in localNRregions]
                    print ("The Regions that needs to be added - ", list_difference)
                    list_difference1 = [item for item in localNRregions if item not in NRregions]
                    print("The Regions that needs to be removed - ", list_difference1)


def calculation_of_CIDR():
    NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
    with requests.get(NR_SYN_URL) as response:
        if response.status_code == 200:
            data = json.loads(response.text)
            NRregions = list(data.keys())
            for REGION in NRregions:
                for i in data[REGION]:
                    i = i + '/32'
                    NR_SG_Entries.append({"Cidr": i})
                print(REGION)
                print(NR_SG_Entries)
                print(len(NR_SG_Entries))
                creation_of_pl(AWS_REGION, NR_SG_Entries, REGION)
                NR_SG_Entries.clear()
                json_editing(prefix_list_ids,REGION)
                prefix_list_ids.clear()



def creation_of_pl(arg_region,arg_plcidr,arg_nrregion):
    session = boto3.Session(profile_name=arg_profile, region_name=arg_region)
    client = session.client('ec2')
    response = client.create_managed_prefix_list(
        PrefixListName=f'AMSBasic-NR_Synthetic_{arg_nrregion}_Monitoring_Allowlisting',
        MaxEntries=24,
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
                        'Value': 'AMSBasic-NR_Synthetic_Monitoring_Allowlisting'
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
    time.sleep(2)
    pl_id = response['PrefixList']['PrefixListId']
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


def json_editing(prefix,reg):
    with open(f'{AWS_REGION}_NR_PL.json', 'r') as j:
        json_data = json.load(j)
        json_data[reg] = prefix
        with open(f'{AWS_REGION}_NR_PL.json', 'w') as x:
            json.dump(json_data, x)




def updating_of_pl():
    NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
    with requests.get(NR_SYN_URL) as response:
        if response.status_code == 200:
            data = json.loads(response.text)
            NRregions = list(data.keys())
            with open(f'{AWS_REGION}_NR_PL.json', 'r') as j:
                json_data = json.load(j)
                localNRregions = list(json_data.keys())
                print(localNRregions)
                print(NRregions)
                if (collections.Counter(NRregions) != collections.Counter(localNRregions)):
                    print("Use the AWS SNS to email that NR Regions have changed - removed / added")
                    list_difference = [item for item in NRregions if item not in localNRregions]
                    print("The Regions that needs to be added - ", list_difference)
                    list_difference1 = [item for item in localNRregions if item not in NRregions]
                    print("The Regions that needs to be removed - ", list_difference1)
                else:
                    with open(f'{AWS_REGION}_NR_PL.json', 'r') as k:
                        json_data1 = json.load(k)
                        localNRregions = list(json_data.keys())
                        for rgn in localNRregions:
                            NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
                            with requests.get(NR_SYN_URL) as response:
                                if response.status_code == 200:
                                    data10 = json.loads(response.text)
                                    for i in data10[rgn]:
                                        i = i + '/32'
                                        NR_SG_Entries.append({"Cidr": i})
                                    for v in json_data1[rgn]:
                                        currentregPL.append(v)
                                    initial = 0
                                    final = 24
                                    for pl in currentregPL:
                                        session1 = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
                                        client1 = session1.client('ec2')
                                        response1 = client1.get_managed_prefix_list_entries(
                                            PrefixListId=pl,
                                        )
                                        for i in response1['Entries']:
                                            prefixListCIDR.append({"Cidr": i['Cidr']})
                                        print(rgn)
                                        print(pl)
                                        print(prefixListCIDR)
                                        session2 = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
                                        client2 = session2.client('ec2')
                                        response2 = client2.describe_managed_prefix_lists(
                                            DryRun=False,
                                            PrefixListIds=[pl]
                                        )
                                        prefixListVersion1 = response2['PrefixLists'][0]['Version']
                                        print(prefixListVersion1)
                                        session3 = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
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
                                        session4 = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
                                        client4 = session4.client('ec2')
                                        response4 = client4.modify_managed_prefix_list(
                                            DryRun=False,
                                            CurrentVersion=prefixListVersion1,
                                            PrefixListId=pl,
                                            AddEntries=NR_SG_Entries[initial:final]
                                        )
                                        initial = initial + 24
                                        final = final + 24
                                    currentregPL.clear()
                                    NR_SG_Entries.clear()





def main():
    global AWS_REGION
    #preparing_sample_json()
    print('Enter the AWS Region ')
    AWS_REGION = str(input(""))
    #Region_Check()
    #calculation_of_CIDR()
    updating_of_pl()



main()