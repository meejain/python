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

base_url = 'https://splunk-api.or1.adobe.net'


def calculate_baseline(hostname, segmentstore, response):
    occurence = 0
    skipgc = []
    postcleanup = []
    floatskipgc = []
    floatpostcleanup = []
    r1 = json.loads(response.text)
    if r1["results"] == []:
        comments = "There are no Online TAR Compaction logs for the instance, hence please check the instance as to why it is NOT SPLUNKING the logs. You can however, further analyse the last Offline Compaction Logs"
    print ()
    print("Target Instance = " + hostname + " and its current Segment Store size is " + segmentstore)
    for a in r1["results"]:
        #print(a["_raw"])
        if "less than sizeDeltaEstimation" in a["_raw"]:
            if occurence == 0:
                occurence = + 1
                comments = "Skipping garbage collection is the latest log"
            indexlow1 = a["_raw"].find("to ")
            indexhigh1 = a["_raw"].find("GB (", indexlow1)
            indexlow1 += 3
            indexhigh1 + - 1
            value1 = a["_raw"][indexlow1:indexhigh1]
            # print ("skip",value1)
            skipgc.append(value1)
        elif ": cleanup completed" in a["_raw"]:
            if occurence == 0:
                occurence = + 1
                comments = "Post cleanup size is the latest log"
            indexlow2 = a["_raw"].find("size is ")
            indexhigh2 = a["_raw"].find("GB (", indexlow2)
            indexlow2 += 8
            indexhigh2 + - 1
            value2 = a["_raw"][indexlow2:indexhigh2]
            # print("post clean up", value2)
            postcleanup.append(value2)
        elif "pre-compaction cleanup" in a["_raw"]:
            pass
        else:
            comments = "There are no Online TAR Compaction logs for the instance, hence please check the instance as to why it is NOT SPLUNKING the logs. You can however, further analyse the last Offline Compaction Logs"
    print("The baseline value analysis for " + hostname + " is as follows - ")
    floatskipgc=[float(x) for x in skipgc]
    floatpostcleanup=[float(x) for x in postcleanup]
    try:
        print("The min. value after skipping garbage collection is " + str(min(floatskipgc)))
        print("The max. value after skipping garbage collection is " + str(max(floatskipgc)))
    except ValueError:
        print("skipping garbage collection logs doesn't exist for this instance")
    try:
        print("The min. value after Post Online Clean up size is " + str(min(floatpostcleanup)))
        print("The max. value after Post Online Clean up size is " + str(max(floatpostcleanup)))
    except ValueError:
        print("Post Online Clean up logs doesn't exist for this instance")
    print(comments)
    if "Skipping garbage collection" in comments:
        print("The latest log value is " + str(floatskipgc[0]))
    elif "Post cleanup size" in comments:
        print("The latest log value is " + str(floatpostcleanup[0]))
    print ()
    print("############################################################Targetting next instance#####################################################")
    print ()


def main():
    sidold = 0
    sid = 0
    username = input("Enter your Splunk userid: ")
    password = maskpass.askpass(prompt="Password:", mask="ha")
    r = requests.get(base_url + "/servicesNS/admin/search/auth/login",
                     data={'username': username, 'password': password}, verify=False)
    try:
        sk = minidom.parseString(r.text).getElementsByTagName('sessionKey')[0].firstChild.nodeValue
    except IndexError:
        pass
    print("Session Key:", sk)
    file1 = open('file1', 'r')
    Lines = file1.readlines()
    line1 = []
    for line in Lines:
        line1 = line.split('\t')
        host = line1[0]
        print (host)
        ss = line1[1]
        #search_query = 'search=search index=ams_cq ' + 'host=' + host + ' source=*crx-quickstart/logs/error.log "*less than sizeDeltaEstimation*" OR "*Post cleanup size*" earliest=-3w@w latest=now'
        #r = requests.post(base_url + '/services/search/jobs/', data=search_query,
                          #headers={'Authorization': ('Splunk %s' % sk)},
                          #verify=False)
        done2 = False
        while not done2:
            print ("Generating Splunk Search ID")
            try:
                search_query = 'search=search index=ams_cq ' + 'host=' + host + ' source=*crx-quickstart/logs/error.log "*less than sizeDeltaEstimation*" OR "*Post cleanup size*" earliest=-3w@w latest=now'
                r = requests.post(base_url + '/services/search/jobs/', data=search_query,
                                  headers={'Authorization': ('Splunk %s' % sk)},
                                  verify=False)
                sid = minidom.parseString(r.text).getElementsByTagName('sid')[0].firstChild.nodeValue
            except IndexError:
                pass
            time.sleep(5)
            print ("Search ID is "+str(sid))
            print ("Old Search ID is "+str(sidold))
            if sid != 0:
                if sid == sidold:
                    done2 = False
                else:
                    done2 = True
            else:
                done2 = False
        sidold=sid
        #print("Search ID", sid)
        done = False
        while not done:
            r = requests.get(base_url + '/services/search/jobs/' + sid,
                             headers={'Authorization': ('Splunk %s' % sk)},
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
        done1 = False
        while not done1:
            print("Generating Request")
            r = requests.get(base_url + '/services/search/jobs/' + sid + '/results/',
                             headers={'Authorization': ('Splunk %s' % sk)},
                             data={'output_mode': 'json'},
                             verify=False)
            time.sleep(5)
            print (r)
            rtest = json.loads(r.text)
            if rtest["messages"][0]["text"] == "call not properly authenticated":
                done1 = False
            else:
                done1 = True
        calculate_baseline(host, ss, r)


main()