import requests
import re
import json
import sys
import time


def preparing_entries_for_NR_SG():
 list1=["No Prefix List allotted"]
 NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
 with requests.get(NR_SYN_URL) as response:
   if response.status_code == 200:
        print('Enter the AWS Region ')
        AWS_REGION = str(input(""))
        data = json.loads(response.text)
        print("Type:", type(data))
        print("The original dictionary is : " + str(data))
        NRregions=list(data.keys())
        with open(f'{AWS_REGION}_NR_PL.json', "w") as outfile:
            json.dump(data, outfile)
        with open(f'{AWS_REGION}_NR_PL.json', 'r') as j:
            json_data = json.load(j)
            for a in NRregions:
                json_data[a]=list1
                with open(f'{AWS_REGION}_NR_PL.json', 'w') as x:
                    json.dump(json_data, x)


def main():
    preparing_entries_for_NR_SG()


main()



















