
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
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
hosts_lists1=[]
hosts_lists=['altec-prod-dispatcher1useast1', 'altec-prod-author1useast1', 'altec-prod-publish1useast1', 'altec-stage1-dispatcher1useast1', 'altec-stage1-author1useast1', 'altec-stage1-publish1useast1']
print(hosts_lists)

for i in hosts_lists:
        if 'prod' in i:
            hosts_lists1.append(i)
print(hosts_lists1);
print(len(hosts_lists1))