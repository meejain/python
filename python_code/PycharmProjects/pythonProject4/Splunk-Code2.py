import os
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
warnings.simplefilter("ignore", UserWarning)
host="orientaltrading-prod1-author1uswest1"
l1=[]
u=input("Enter your Splunk userid: ")
p = maskpass.askpass(prompt="Password:", mask="haha")
#p=getpass.getpass(prompt='Password: ', stream=None)

s = requests.Session()
try:
    r = s.post('https://splunk-api.or1.adobe.net/services/auth/login', data = {'username':u,'password':p}, timeout=10.0)
except requests.exceptions.Timeout as e:
    print(e)
    print("\n" + "Your VPN might not be connected !! ")
    sys.exit(1)
try:
	session_key = xmltodict.parse(r.text)['response']['sessionKey']

except KeyError:
	print("Warning !!! Wrong Credentials Entered")
	sys.exit(1)
headers = {'Authorization':'Splunk ' + session_key}

print("\n"+ "Please wait ... it will take time to fetch data from Splunk...")
param="*after Compact*"

query = {'search': 'search ' + ' index=ams_cq' + ' host=' + host + ' source = /mnt/crx/*/crx-quickstart/logs/oak-tar-compact*.log ' + param + ' earliest=-2mon@mon latest=now | head 1', 'output_mode':'json'}
r2 = s.post('https://splunk-api.or1.adobe.net/servicesNS/admin/search/search/jobs/export', data=query,headers=headers).json()
r3 = r2.items()
newDict = dict()
for key,value in r3:
	if key == 'result':
		newDict[key] = value
x=newDict["result"]["_raw"]
l1=x.split(": ")
print(l1[1])


