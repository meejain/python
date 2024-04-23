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
    sys.exit("USAGE: python azure_whitelisting_2ndapproach.py [aws-profile] [aws-region] [vpc-id]")
else:
    # gov us-gov-west-1 sg-05a6b562 tcp 443 443 HTTPS
    arg_profile = sys.argv[1]
    arg_region = sys.argv[2]
    arg_vpc_id = sys.argv[3]

serviceTagCIDR = []


def preparing_list_Azure_US_East():
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
                serviceTagCIDR.append(address)
      else:
        print('An error occurred while attempting to retrieve json data from Microsoft.')
  else:
    print('An error occurred while attempting to retrieve data from Microsoft.')
 print(serviceTagCIDR)
 print(len(serviceTagCIDR))


def calculate_no_of_SG():
    global noofSG
    global size
    size=len(serviceTagCIDR)
    rem=size%60
    quot=size//60
    if rem > 0:
        noofSG=quot+1
    else:
        noofSG=quot
    print('The No. of Security Groups that needs to be Created are %s.' % (noofSG))


def creationofSGs(cidr,vpcid):
    global GrpName
    global security_group_id
    initial=0
    final=60
    session = boto3.Session(profile_name=arg_profile, region_name=arg_region)
    client = session.client('ec2')
    for x in range(1,noofSG+1):
        print('Enter the name of %s Security Group' % (x))
        GrpName = str(input(""))
        response = client.create_security_group(
            Description='Testing',
            GroupName=GrpName,
            VpcId=vpcid,
            DryRun=False
        )
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpcid))
        sgcidr=cidr[initial:final]
        for Address in sgcidr:
            data = client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': 'tcp',
                     'FromPort': 443,
                     'ToPort': 443,
                     'IpRanges': [{'CidrIp': Address}]},
                ])
        print('Ingress Successfully Set %s' % data)
        initial=initial+60
        final=final+60





def main():
    preparing_list_Azure_US_East()
    calculate_no_of_SG()
    creationofSGs(serviceTagCIDR[0:],arg_vpc_id)


main()