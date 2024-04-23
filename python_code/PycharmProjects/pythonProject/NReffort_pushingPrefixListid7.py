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


def appending_of_pl():
    with open(f'{AWS_REGION}_NR_PL.json', 'r') as k:
        json_data1 = json.load(k)
        localNRregions = list(json_data1.keys())
        for rgn in localNRregions:
            for v in json_data1[rgn]:
                currentregPL.append(v)
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
                print (len(prefixListCIDR))
                prefixListCIDR.clear()
                session2 = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
                client2 = session2.client('ec2')
                response2 = client2.describe_managed_prefix_lists(
                    DryRun=False,
                    PrefixListIds=[pl]
                )
                prefixListVersion1 = response2['PrefixLists'][0]['Version']
                with open('new_NR_IP_range.json', 'r') as l:
                    json_data11 = json.load(l)
                    for x in json_data11[rgn]:
                        new_NR_SG_Entries.append({"Cidr": x})
                    print(new_NR_SG_Entries)
                    session5 = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
                    client5 = session5.client('ec2')
                    response5 = client5.modify_managed_prefix_list(
                        DryRun=False,
                        CurrentVersion=prefixListVersion1,
                        PrefixListId=pl,
                        RemoveEntries=new_NR_SG_Entries
                    )
                    new_NR_SG_Entries.clear()
            currentregPL.clear()







def main():
    global AWS_REGION
    print('Enter the AWS Region ')
    AWS_REGION = str(input(""))
    appending_of_pl()


main()