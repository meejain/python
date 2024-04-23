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
if(len(sys.argv) != 4):
    sys.exit("USAGE: python aws_pl_from_azure.py [aws-profile] [aws-region] [prefix-list-id]")
else:
    # gov us-gov-west-1 sg-05a6b562 tcp 443 443 HTTPS
    arg_profile = sys.argv[1] # gov
    arg_region = sys.argv[2] # us-gov-west-1
    arg_pl_id = sys.argv[3] # sg-05868462
serviceTagCIDR = []
prefixListVersion = int()
prefixListCIDR = []
def get_service_tag_ip_array():
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
  print (serviceTagCIDR)
def get_prefix_list_version(prefixlist):
  global prefixListVersion
  session = boto3.Session(profile_name=arg_profile,region_name=arg_region)
  client = session.client('ec2')
  response = client.describe_managed_prefix_lists(
    DryRun=False,
    PrefixListIds=[ prefixlist ]
  )
  prefixListVersion = response['PrefixLists'][0]['Version']
def get_current_ip_array(prefixlist):
  session1 = boto3.Session(profile_name=arg_profile,region_name=arg_region)
  client1 = session1.client('ec2')
  response1 = client1.get_managed_prefix_list_entries(
    PrefixListId=prefixlist,
  )
  for i in response1['Entries']:
    prefixListCIDR.append({"Cidr": i['Cidr']})
def remove_entries(prefixlist, cidr):
  global prefixListVersion
  session = boto3.Session(profile_name=arg_profile,region_name=arg_region)
  client = session.client('ec2')
  response = client.modify_managed_prefix_list(
    DryRun=False,
    CurrentVersion=prefixListVersion,
    PrefixListId=prefixlist,
    RemoveEntries=cidr
  )
  prefixListVersion += 1
  print(response)
def add_entries(prefixlist, cidr):
  global prefixListVersion
  session = boto3.Session(profile_name=arg_profile,region_name=arg_region)
  client = session.client('ec2')
  response = client.modify_managed_prefix_list(
    DryRun=False,
    CurrentVersion=prefixListVersion,
    PrefixListId=prefixlist,
    AddEntries=cidr
  )
  prefixListVersion += 1
  print(response)
def main():
  get_service_tag_ip_array()
  get_prefix_list_version(arg_pl_id)
  get_current_ip_array(arg_pl_id)
  if len(prefixListCIDR) > 0 :
    remove_entries(arg_pl_id,prefixListCIDR[:100])
    time.sleep(10)
  get_prefix_list_version(arg_pl_id)
  get_current_ip_array(arg_pl_id)
  if len(prefixListCIDR) > 100 :
    remove_entries(arg_pl_id,prefixListCIDR[100:])
  if len(prefixListCIDR) > 0 :
    print("Waiting for Removals")
    time.sleep(10)
  if len(serviceTagCIDR) > 0 :
    add_entries(arg_pl_id,serviceTagCIDR[:100])
  if len(serviceTagCIDR) > 100 :
    add_entries(arg_pl_id,serviceTagCIDR[100:])
main()
#print(serviceTagCIDR)
#print(len(serviceTagCIDR))
#print(prefixListCIDR)
#print(len(prefixListCIDR))