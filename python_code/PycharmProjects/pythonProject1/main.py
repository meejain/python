import requests
import re
import json
SERVICE_TAGS_URL = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'
SERVICE_TAG = 'AzureCloud.eastus'
serviceTagCIDR = []
with requests.get(SERVICE_TAGS_URL) as response:
  if response.status_code == 200:
    with requests.get(re.search('https://download.*?\.json', response.text).group()) as servicetagjson:
      if servicetagjson.status_code == 200:
        data = json.loads(servicetagjson.text)
        for i in data['values']:
          if SERVICE_TAG.lower() == i['name'].lower():
            for address in i['properties']['addressPrefixes']:
              if not "::" in address:
                serviceTagCIDR.append(address)
      else:
        print('An error occurred while attempting to retrieve json data from Microsoft.')
  else:
    print('An error occurred while attempting to retrieve data from Microsoft.')
print(serviceTagCIDR)
print(len(serviceTagCIDR))