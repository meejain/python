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
    sys.exit("USAGE: python new_relic_whitelisting.py [aws-profile] [aws-region] [vpc-id]")
else:
    # gov us-gov-west-1 sg-05a6b562 tcp 443 443 HTTPS
    arg_profile = sys.argv[1]
    arg_region = sys.argv[2]
    arg_vpc_id = sys.argv[3]

NR_SG_Entries = []
IP: str = '0.0.0.0/0'

def preparing_entries_for_NR_SG():
 NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
 with requests.get(NR_SYN_URL) as response:
   if response.status_code == 200:
        data = json.loads(response.text)
        for x in range(1,6):
         print('Enter the Region ',x)
         REGION=str(input(""))
         for i in data[REGION]:
          i=i+'/32'
          NR_SG_Entries.append(i)
   else:
     print('An error occurred while attempting to retrieve data from Microsoft.')
 print(NR_SG_Entries)
 print(len(NR_SG_Entries))
 print("Removing the Duplicate IP's ")
 NR_SG_Entries=list(dict.fromkeys(NR_SG_Entries))



def create_Security_Group(vpcid):
    global GrpName
    global security_group_id
    session = boto3.Session(profile_name=arg_profile, region_name=arg_region)
    client = session.client('ec2')
    print("Enter the name of the Security Group")
    GrpName = str(input(""))
    response = client.create_security_group(
        Description='Testing',
        GroupName=GrpName,
        VpcId=vpcid,
        DryRun=False
    )
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpcid))


def update_Security_Group(sgid,cidr):
    session = boto3.Session(profile_name=arg_profile, region_name=arg_region)
    client = session.client('ec2')
    for Address in cidr:
        data = client.authorize_security_group_ingress(
            GroupId=sgid,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 443,
                 'ToPort': 443,
                 'IpRanges': [{'CidrIp': Address}]},
            ])
    print('Ingress Successfully Set %s' % data)



def main():
    preparing_entries_for_NR_SG()
    create_Security_Group(arg_vpc_id)
    update_Security_Group(security_group_id,NR_SG_Entries[0:])

main()
