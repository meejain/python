# Need to install requests package for python
# easy_install requests
import requests
import re
import json
import sys
import time
import collections
import matplotlib.pyplot as plt

imsorg = []
customername = []
imsorgforms = []
customernameforms = []
nodata =[]
cscore = []
finalimsorgid = []
finalcustname = []
enddate = []
enddateforms = []
nodestoresize=268435456000
jcrnodes=55000000
noofassets=4500000
custblocknodestoresize = []
custblockjcrnodes = []
custblocknoofassets = []
Low=0
LowMedium=0
Medium=0
MediumHigh=0
High=0
ExtremelyHigh=0
blocked=0
incompletestats = []
contractenddate = []
d2="2022-12-31"
lowhangingfruits = []
Lowcust = []
LowMediumcust = []
Mediumcust = []

url = 'https://adobedev.service-now.com/api/now/table/core_company?sysparm_query=u_active%3Dtrue%5Eu_product%3DAEM%20Basic%5Eu_status!%3DPre-Sale%5Eu_status!%3DNo%20deal%5Eu_status!%3DTerminated%5E&sysparm_display_value=true&sysparm_fields=name%2Cu_customer_success_engineer%2Cu_ims_org_id%2Cu_aem_forms%2Cu_end_date'

user = 'cae_rest'
pwd = 'Adobe@1234'

# Set proper headers
headers = {"Content-Type": "application/json", "Accept": "application/json"}

# Do the HTTP request
response = requests.get(url, auth=(user, pwd), headers=headers)

# Check for HTTP codes other than 200
if response.status_code != 200:
    print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
    exit()

# Decode the JSON response into a dictionary and use the data
data = response.json()
json_string = json.dumps(data)
#print(json_string)

for i in data['result']:
    imsorg.append(i['u_ims_org_id'])
    customername.append(i['name'])
    enddate.append(i['u_end_date'])
    if i['u_aem_forms'] == "true":
        imsorgforms.append(i['u_ims_org_id'])
        customernameforms.append(i['name'])
        enddateforms.append(i['u_end_date'])

imsorgid=imsorg
custname=customername
contractenddate=enddate

print(imsorgid)


for ims in imsorgid:
    if(not ims):
        continue
    headers = {
        'accept': 'application/json',
    }
    files = {
        'search': (None, f'imsOrgId:{ims}'),
    }
    response = requests.post('https://aemcloudadoptionqueryservice-va7.cloud.adobe.io/query', headers=headers,
                             files=files)
    customerdata = response.json()
    indx = imsorgid.index(ims)
    if customerdata["projectCount"] == 0:
       # print (ims,"=","Data not available in CAM Database")
        nodata.append(custname[indx])
        continue
    try:
        customerdata["reports"][0]["overview"]["nodeStoreSize"]
    except KeyError:
        print("nodeStoreSize doesn't exist for ", custname[indx])
    else:
        if customerdata["reports"][0]["overview"]["nodeStoreSize"] > nodestoresize:
            custblocknodestoresize.append(custname[indx])
            continue
    try:
        customerdata["reports"][0]["overview"]["totalNodeCount"]
    except KeyError:
        print("totalNodeCount doesn't exist for ", custname[indx])
    else:
        if customerdata["reports"][0]["overview"]["totalNodeCount"] > jcrnodes:
            custblockjcrnodes.append(custname[indx])
            continue
    try:
        customerdata["reports"][0]["overview"]["assetCount"]
    except KeyError:
        print("assetCount doesn't exist for ", custname[indx])
    else:
        if customerdata["reports"][0]["overview"]["assetCount"] > noofassets:
            custblocknoofassets.append(custname[indx])
            continue
    print(ims,"=",customerdata["reports"][0]["overview"]["overallComplexity"], " | Contract End Date - ", contractenddate[indx])
    d1=contractenddate[indx]
    d3 = time.strptime(d1, "%Y-%m-%d")
    d4 = time.strptime(d2, "%Y-%m-%d")
    if customerdata["reports"][0]["overview"]["overallComplexity"] <= 1.15:
        Lowcust.append(custname[indx])
        if d4 > d3:
            lowhangingfruits.append(custname[indx])
    elif customerdata["reports"][0]["overview"]["overallComplexity"] > 1.15 and customerdata["reports"][0]["overview"]["overallComplexity"] <= 1.61:
        LowMediumcust.append(custname[indx])
        if d4 > d3:
            lowhangingfruits.append(custname[indx])
    elif customerdata["reports"][0]["overview"]["overallComplexity"] > 1.61 and customerdata["reports"][0]["overview"]["overallComplexity"] <= 2.07:
        Mediumcust.append(custname[indx])
        if d4 > d3:
            lowhangingfruits.append(custname[indx])
    cscore.append(customerdata["reports"][0]["overview"]["overallComplexity"])
    finalimsorgid.append(ims)
    finalcustname.append(custname[indx])



for a in cscore:
    if a <= 1.15:
        Low+=1
    elif a > 1.15 and a <= 1.61:
        LowMedium+=1
    elif a > 1.61 and a <= 2.07:
        Medium+=1
    elif a > 2.07 and a <= 2.53:
        MediumHigh+=1
    elif a > 2.53 and a <= 2.99:
        High+=1
    elif a > 2.99:
        ExtremelyHigh+=1

blocked=len(custblocknodestoresize)+len(custblockjcrnodes)+len(custblocknoofassets)
x=["Low","Low Medium","Medium","MediumHigh","High","ExtremelyHigh","Not in CAM Database", "Currently Blocked"]
h=[Low,LowMedium,Medium,MediumHigh,High,ExtremelyHigh,len(nodata),blocked]
c=["blue","lightblue","green","lightgreen","orange","red","grey","black"]
plt.bar(x,h,width=1,color=c)
plt.xlabel("BPA Complexity Score")
plt.ylabel("Basic Forms Customers")
plt.title("BPA Complexity Distribution")
plt.text(0,Low,Low,ha="center",va="bottom")
plt.text(1,LowMedium,LowMedium,ha="center",va="bottom")
plt.text(2,Medium,Medium,ha="center",va="bottom")
plt.text(3,MediumHigh,MediumHigh,ha="center",va="bottom")
plt.text(4,High,High,ha="center",va="bottom")
plt.text(5,ExtremelyHigh,ExtremelyHigh,ha="center",va="bottom")
plt.text(6,len(nodata),len(nodata),ha="center",va="bottom")
plt.text(7,blocked,blocked,ha="center",va="bottom")
plt.show()



print("Customers for whom BPA needs to be rerun & uploaded onto the CAM - ",nodata)
print("Customers which are Blocked: ", "High Node Store Size - ", custblocknodestoresize, "High JCR Nodes - ",custblockjcrnodes,"High No of Assets - ", custblocknoofassets)
print("The no. of customers having the max. Probability for their move to CS: ", len(lowhangingfruits))
print("They are - ", lowhangingfruits)





