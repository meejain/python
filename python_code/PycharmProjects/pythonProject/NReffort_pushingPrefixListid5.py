import requests
import re
import json
import sys
import time
import collections



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
                    with open(f'{AWS_REGION}_NR_PL.json', 'r') as j:
                        json_data = json.load(j)
                        for a in list_difference:
                            print('Enter the prefixlist for region', a)
                            pllist = str(input(""))
                            list1 = [pllist]
                            json_data[a] = list1
                            with open(f'{AWS_REGION}_NR_PL.json', 'w') as x:
                                json.dump(json_data, x)



                    list_difference1 = [item for item in localNRregions if item not in NRregions]
                    print("The Regions that needs to be removed - ", list_difference1)
                else:
                    print("All regions up to date")





def main():
    global AWS_REGION
    print('Enter the AWS Region ')
    AWS_REGION = str(input(""))
    updating_of_pl()


main()

