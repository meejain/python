import os
import time
import ntpath
import sys
import json
import requests
import pandas as pd
import getpass
import xmltodict
import warnings
from datetime import date
import maskpass
from xml.dom import minidom
from requests.packages.urllib3.exceptions import InsecureRequestWarning


skipgc = []
postcleanup =[]

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

base_url = 'https://splunk-api.or1.adobe.net'
username = 'meejain'
password = 'wanderlusthnm@123456789'
i=0
occurence=0











hostname="maisobatta-prod1-author1francecentral"
search_query = 'search=search index=ams_cq '+'host='+hostname+' source=*crx-quickstart/logs/error.log "*less than sizeDeltaEstimation*" OR "*Post cleanup size*" earliest=-3w@w latest=now'

r = requests.get(base_url + "/servicesNS/admin/search/auth/login",
                 data={'username': username, 'password': password}, verify=False)

session_key = minidom.parseString(r.text).getElementsByTagName('sessionKey')[0].firstChild.nodeValue
print("Session Key:", session_key)

r = requests.post(base_url + '/services/search/jobs/', data=search_query,
                  headers={'Authorization': ('Splunk %s' % session_key)},
                  verify=False)
time.sleep(5)
try:
    sid = minidom.parseString(r.text).getElementsByTagName('sid')[0].firstChild.nodeValue
except IndexError:
    pass
time.sleep(10)
#print("Search ID", sid)
done = False
while not done:
    r = requests.get(base_url + '/services/search/jobs/' + sid,
                     headers={'Authorization': ('Splunk %s' % session_key)},
                     verify=False)
    response = minidom.parseString(r.text)
    for node in response.getElementsByTagName("s:key"):
        if node.hasAttribute("name") and node.getAttribute("name") == "dispatchState":
            dispatchState = node.firstChild.nodeValue
            print("Search Status: ", dispatchState)
            if dispatchState == "DONE":
                done = True
            else:
                time.sleep(1)

r = requests.get(base_url + '/services/search/jobs/' + sid + '/results/',
                 headers={'Authorization': ('Splunk %s' % session_key)},
                 data={'output_mode': 'json'},
                 verify=False)

r1 = json.loads(r.text)
print (r1)
if r1["results"] == []:
    print ("There are no Online TAR Compaction logs for the instance, hence checking the last Offline Compaction Logs")

time.sleep(5)
for a in r1["results"]:
    print (a["_raw"])
    if "less than sizeDeltaEstimation" in a["_raw"]:
        if occurence == 0:
            occurence =+ 1
            comments="Skipping garbage collection is the latest log"
        indexlow1=a["_raw"].find("to ")
        indexhigh1=a["_raw"].find("GB (",indexlow1)
        indexlow1 += 3
        indexhigh1 +- 1
        value1=a["_raw"][indexlow1:indexhigh1]
        #print ("skip",value1)
        skipgc.append(value1)
    elif ": cleanup completed" in a["_raw"]:
        if occurence == 0:
            occurence =+ 1
            comments="Post cleanup size is the latest log"
        indexlow2 = a["_raw"].find("size is ")
        indexhigh2 = a["_raw"].find("GB (", indexlow2)
        indexlow2 += 8
        indexhigh2 + - 1
        value2 = a["_raw"][indexlow2:indexhigh2]
        #print("post clean up", value2)
        postcleanup.append(value2)
    elif "pre-compaction cleanup" in a["_raw"]:
        pass
    else:
        comments="There are no Online TAR Compaction logs for the instance, hence checking the last Offline Compaction Logs"
print ("########################################################################################################################################################")
print ("The baseline value analysis for "+hostname+" is as follows - ")
try:
    print("The min. value after skipping garbage collection is " + min(skipgc))
    print("The max. value after skipping garbage collection is " + max(skipgc))
except ValueError:
    print("skipping garbage collection logs doesn't exist for this instance")
try:
    print("The min. value after Post Online Clean up size is " + min(postcleanup))
    print("The max. value after Post Online Clean up size is " + max(postcleanup))
except ValueError:
    print("Post Online Clean up logs doesn't exist for this instance")
print (comments)
if "Skipping garbage collection" in comments:
    print ("The latest log value is "+skipgc[0])
elif "Post cleanup size" in comments:
    print("The latest log value is " + postcleanup[0])





    #print(a["_raw"])



