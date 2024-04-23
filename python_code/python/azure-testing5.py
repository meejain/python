from azure.identity import ClientSecretCredential
from azure.identity import DefaultAzureCredential
from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.v2020_06_01.models import NetworkSecurityGroup
from azure.mgmt.network.v2020_06_01.models import SecurityRule


subscription_id = "c3068f45-6a31-487c-bd27-58907a0131a1"

credential = AzureCliCredential()

network_client = NetworkManagementClient(credential, subscription_id)

resource_group_name = "Meet-Python-Testing"
nsg_name = "test-nr-monitoring"
new_security_rule_name = "testing6"

address=['15.86.0.0/16','15.34.65.34/32','15.84.67.54/32']

async_security_rule = network_client.security_rules.begin_create_or_update( 
     resource_group_name, 
     nsg_name, 
     new_security_rule_name, 
     { 
             'access':'Allow', 
             'description':'New Test security rule', 
             'destination_address_prefix':'20.26.0.0/16', 
             'destination_port_range':'8080', 
             'direction':'Inbound', 
             'priority':4000, 
             'protocol':'Tcp', 
             'source_address_prefixes':address, 
             'source_port_range':'*', 
     } 
)
