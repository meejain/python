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
# Display if not all variables are displayed

NR_SG_Entries = []
IP: str = '0.0.0.0/0'
arg_profile='bpbu17'

def preparing_entries_for_NR_SG():
 NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
 with requests.get(NR_SYN_URL) as response:
   if response.status_code == 200:
        data = json.loads(response.text)
        for x in range(1,6):
         NR_SG_Entries = []
         print('Enter the Region ',x)
         REGION=str(input(""))
         for i in data[REGION]:
          i=i+'/32'
          NR_SG_Entries.append({"Cidr": i})
         print(NR_SG_Entries)
         print(len(NR_SG_Entries))
         #print("Removing the Duplicate IP's ")
         #NR_SG_Entries = list(dict.fromkeys(NR_SG_Entries))

   else:
     print('An error occurred while attempting to retrieve data from Microsoft.')



def main():
    preparing_entries_for_NR_SG()


main()
