import requests
import re
import json
import sys
import time
from datetime import date
import difflib

serviceTagCIDR = []


def test():
    print("hey buddy")


def preparing_list_Azure_US_East():
 global today
 SERVICE_TAGS_URL = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'
 SERVICE_TAG = 'AzureCloud.eastus'
 with requests.get(SERVICE_TAGS_URL) as response:
  if response.status_code == 200:
    with requests.get(re.search('https://download.*?\.json', response.text).group()) as servicetagjson:
      if servicetagjson.status_code == 200:
        data = json.loads(servicetagjson.text)
        for i in data['values']:
          if SERVICE_TAG.lower() == i['name'].lower():
            for address in i['properties']['addressPrefixes']:
              if not "::" in address:
                serviceTagCIDR.append({"Cidr": address})
      else:
        print('An error occurred while attempting to retrieve json data from Microsoft.')
  else:
    print('An error occurred while attempting to retrieve data from Microsoft.')
 print(serviceTagCIDR)
 print(len(serviceTagCIDR))
 today = date.today()
 print(today)
 f1 = open(f'{today}.json', 'w')
 f1.write(json.dumps(serviceTagCIDR))
 f1.close()

def sorting(item):
    if isinstance(item, dict):
        return sorted((key, sorting(values)) for key, values in item.items())
    if isinstance(item, list):
        return sorted(sorting(x) for x in item)
    else:
        return item

def comparejson():
    print('Enter the json file name to be compared with ')
    old_file = str(input(""))
    with open(f'{old_file}', 'r') as x:
        json_data = json.load(x)
    with open(f'{today}.json', 'r') as y:
        json_data1 = json.load(y)
    result=sorting(json_data) == sorting(json_data1)
    print (result)
    if result == False:
        print ("hey")
    print("The differences are - ")
    with open(f'{old_file}') as file_1:
        file_1_text = file_1.readlines()
    with open(f'{today}.json') as file_2:
        file_2_text = file_2.readlines()
    for line in difflib.unified_diff(
            file_1_text, file_2_text, fromfile='file1.txt',
            tofile='file2.txt', lineterm=''):
        print(line)



def main():
    preparing_list_Azure_US_East()
    comparejson()


main()