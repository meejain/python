import requests
import re
import json
import sys
import time
import collections

headers = {
    'accept': 'application/json',
    # requests won't add a boundary if this header is set when you pass files=
    # 'Content-Type': 'multipart/form-data',
}

files = {
    'search': (None, 'imsOrgId:6E110E835D68E2FF0A495C82@AdobeOrg'),
}

response = requests.post('https://aemcloudadoptionqueryservice-va7.cloud.adobe.io/query', headers=headers, files=files)
print(response.json())
