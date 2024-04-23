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
  with open('new_NR_IP_range_oct22.json', 'r') as l:
        data = json.load(l)
        NR_SG_Entries = []
        for x in range(1,6):
         print('Enter the Region ')
         REGION=str(input(""))
         for i in data[REGION]:
           NR_SG_Entries.append(i)
        print("The Final List of subnets are : ")
        print(NR_SG_Entries)
        print(len(NR_SG_Entries))
        update_NR_NSG(NR_SG_Entries)
      

     

def update_NR_NSG(address):
 print('Enter the subscription id ')
 subscription_id=str(input(""))
 credential = AzureCliCredential()
 network_client = NetworkManagementClient(credential, subscription_id)
 print('Enter the resource group ')
 resource_group_name=str(input(""))
 print('Enter the NSG name ')
 nsg_name=str(input(""))
 new_security_rule_name = "new_relic_monitoring_subnets1"
 async_security_rule = network_client.security_rules.begin_create_or_update( 
     resource_group_name, 
     nsg_name, 
     new_security_rule_name, 
     { 
             'access':'Allow', 
             'description':'New Test security rule', 
             'destination_address_prefix':'*', 
             'destination_port_range':'443', 
             'direction':'Inbound', 
             'priority':3050, 
             'protocol':'Tcp', 
             'source_address_prefixes':address, 
             'source_port_range':'*', 
     } 
 )

def main():
    preparing_entries_for_NR_SG()


main()
