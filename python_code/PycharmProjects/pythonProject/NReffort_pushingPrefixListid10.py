import requests
import re
import json
import sys
import time
import collections

NR_SG_Entries = []
prefix_list_ids = []
arg_profile='bpbu12'


try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    sys.exit("Could not import 'boto3', please install this package.")



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


def main():
    global AWS_REGION
    print('Enter the AWS Region ')
    AWS_REGION = str(input(""))
    calculation_of_CIDR()



main()
