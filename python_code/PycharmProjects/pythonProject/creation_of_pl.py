import requests
import re
import json
import sys
import time
import collections

NR_SG_Entries = []
prefix_list_ids = []
arg_profile='bpbu18'
currentregPL = []
presentlist = ['52.226.0.192/28', '52.226.0.208/28', '20.54.169.208/28', '20.29.152.16/28', '20.252.85.176/28', '20.121.88.208/30', '20.252.12.4/30']
finallist = []


try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    sys.exit("Could not import 'boto3', please install this package.")


def creation_of_pl():
        session = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
        client = session.client('ec2')
        response = client.create_managed_prefix_list(
            PrefixListName='AMSBasic-CM_Dedicated_IPs_Allowlisting',
            MaxEntries=7,
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
                            'Value': 'AMSBasic-CM_Dedicated_IPs_Allowlisting'
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
        time.sleep(5)
        pl_id = response['PrefixList']['PrefixListId']
        prefixListVersion = response['PrefixList']['Version']
        print (pl_id, prefixListVersion)
        for i in presentlist:
            finallist.append({"Cidr": i})
        response = client.modify_managed_prefix_list(
            DryRun=False,
            PrefixListId=pl_id,
            CurrentVersion=prefixListVersion,
            AddEntries=finallist
        )




def main():
    global AWS_REGION
    # preparing_sample_json()
    print('Enter the AWS Region ')
    AWS_REGION = str(input(""))
    creation_of_pl()


main()