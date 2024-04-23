import requests
import re
import json
import sys
import time
import collections

ims="BA3E5257595416580A495C6D@AdobeOrg"
headers = {
        'accept': 'application/json',
    }
files = {
        'search': (None, f'imsOrgId:{ims}'),
    }
response = requests.post('https://aemcloudadoptionqueryservice-va7.cloud.adobe.io/query', headers=headers,
                             files=files)
customerdata = response.json()
print (customerdata["projectCount"])
if customerdata["projectCount"] == 0:
    print ("deed")




