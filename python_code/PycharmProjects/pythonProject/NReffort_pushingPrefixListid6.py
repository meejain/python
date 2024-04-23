import requests
import re
import json
import sys
import time
import collections

NR_SG_Entries = []
currentregPL = []
arg_profile='bpbu12'
prefixListCIDR = []
new_NR_SG_Entries = []


try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    sys.exit("Could not import 'boto3', please install this package.")



def updating_of_pl():
    global size
    size = 0
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
                        localNRregions = list(json_data1.keys())
                        for rgn in localNRregions:
                            NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
                            with requests.get(NR_SYN_URL) as response:
                                if response.status_code == 200:
                                    data10 = json.loads(response.text)
                                    for i in data10[rgn]:
                                        size = size + 1
                                        if i.find("/") == -1:
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
                                        prefixListVersion1 += 1
                                        print("Addition in process")
                                        print(response4)
                                        time.sleep(10)
                                        append_new_IPs(rgn, pl, prefixListVersion1, size)
                                        initial = initial + 24
                                        final = final + 24
                                    currentregPL.clear()
                                    NR_SG_Entries.clear()


def append_new_IPs(new_rgn,new_pl,new_prefixListVersion,new_size):
    with open('new_NR_IP_range.json', 'r') as l:
        json_data11 = json.load(l)
        for x in json_data11[new_rgn]:
            new_NR_SG_Entries.append({"Cidr": x})
        print (new_NR_SG_Entries)
        session5 = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
        client5 = session5.client('ec2')
        response5 = client5.modify_managed_prefix_list(
                                            DryRun=False,
                                            CurrentVersion=new_prefixListVersion,
                                            PrefixListId=new_pl,
                                            AddEntries=new_NR_SG_Entries[0:5]
                                        )
        new_NR_SG_Entries.clear()



def main():
    global AWS_REGION
    print('Enter the AWS Region ')
    AWS_REGION = str(input(""))
    updating_of_pl()


main()