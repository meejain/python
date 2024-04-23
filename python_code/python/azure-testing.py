from azure.identity import ClientSecretCredential
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.v2020_06_01.models import NetworkSecurityGroup
from azure.mgmt.network.v2020_06_01.models import SecurityRule


subscription_id = "c3068f45-6a31-487c-bd27-58907a0131a1"

credential = DefaultAzureCredential()

network_client = NetworkManagementClient(credential, subscription_id)

resource_group_name = "Meet-Python-Testing"
nsg_name = "testnsg"

nsg_params = NetworkSecurityGroup(id= "testnsg", location="UK South", tags={ "name" : "testnsg" })
nsg = network_client.network_security_groups.begin_create_or_update(resource_group_name, "testnsg", parameters=nsg_params)
print(nsg.result().as_dict())
