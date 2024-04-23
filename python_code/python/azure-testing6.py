from azure.identity import ClientSecretCredential
from azure.identity import DefaultAzureCredential
from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.v2020_06_01.models import NetworkSecurityGroup
from azure.mgmt.network.v2020_06_01.models import SecurityRule
import requests
import re
import json
import sys
import time



def preparing_entries_for_NR_SG():
 NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
 with requests.get(NR_SYN_URL) as response:
   if response.status_code == 200:
        data = json.loads(response.text)
        NR_SG_Entries = []
        for x in range(1,6):
         print('Enter the Region ',x)
         REGION=str(input(""))
         for i in data[REGION]:
          i=i+'/32'
          NR_SG_Entries.append(i)
        print("The Final List of subnets are : ")
        print(NR_SG_Entries)
        print(len(NR_SG_Entries))
        update_NR_NSG(NR_SG_Entries)
         
         

   else:
     print('An error occurred while attempting to retrieve data from Microsoft.')

     

def update_NR_NSG(address):
 subscription_id = "c3068f45-6a31-487c-bd27-58907a0131a1"
 credential = AzureCliCredential()
 network_client = NetworkManagementClient(credential, subscription_id)
 resource_group_name = "Meet-Python-Testing"
 nsg_name = "test-nr-monitoring"
 new_security_rule_name = "new_relic_monitoring_subnets"
 async_security_rule = network_client.security_rules.begin_create_or_update( 
     resource_group_name, 
     nsg_name, 
     new_security_rule_name, 
     { 
             'access':'Allow', 
             'description':'New Test security rule', 
             'destination_address_prefix':'20.26.0.0/16', 
             'destination_port_range':'443', 
             'direction':'Inbound', 
             'priority':4000, 
             'protocol':'Tcp', 
             'source_address_prefixes':address, 
             'source_port_range':'*', 
     } 
 )

def main():
    preparing_entries_for_NR_SG()


main()
