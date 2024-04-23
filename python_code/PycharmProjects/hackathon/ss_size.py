#!/usr/bin/env python3.10

import csv
import datetime
import json
import gspread
import pandas as pd
import subprocess
import sys
import requests
import warnings
import shutil
import os
from appscript import app, k
# from google.oauth2.service_account import Credentials
# from gspread_pandas import Spread, Client
from gspread_dataframe import set_with_dataframe
from gspread_formatting.dataframe import format_with_dataframe
# from gspread import authorize
from mactypes import Alias
from pathlib import Path
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from time import sleep
from xml.dom import minidom


warnings.simplefilter("ignore", UserWarning)


def original_gen():
    subprocess.call(['./ss_size.sh'])
    original_exists = os.path.exists(original)
    if original_exists:
        # pass
        print('File exists')
        with open(original, 'r') as o:
            for line in o:
                data.append(line.replace('\\t', ' ').replace('\n', ''))
        
    else:
        print('File doesnt exist.  Please troubleshoot why there is no original file.txt.  Exiting program.')
        exit(0)


def csv_create():
    with open(f'{cwd}/AMS-Basic-PROD-Instances-SegmentStoreSize-DiskSpaceUtilization.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header_csv)
        writer.writerows(res_data)


def team_email():
    outlook = app('Microsoft Outlook')
    msg = outlook.make(
		new=k.outgoing_message,
		with_properties={
			k.subject: f'AMS Basic - Segment Store Offenders-{date}',
			k.plain_text_content: f'Attached is this weeks offenders.'})
    msg.make(
		new=k.recipient,
		with_properties={
			k.email_address: {
				k.name: 'DL-ManServ-CEE',
				k.address: 'ManServ-CEA@adobe.com'}})
    p = Alias(str(f'{cwd}/AMS-Basic-PROD-Instances-SegmentStoreSize-DiskSpaceUtilization.csv'))
    q = Alias(str(f'{cwd}/AMS-Basic-PROD-Instances-SegmentStoreSize-DiskSpaceUtilization.txt'))
    msg.make(
		new=k.attachment,
		with_properties={
			k.file: p})
    msg.make(
		new=k.attachment,
		with_properties={
			k.file: q})
    msg.open()
    msg.activate()


def splunk():
    sidold = 0
    sid = 0
    # username = input("Enter your Splunk userid: ")
    # password = maskpass.askpass(prompt="Password:", mask="ha")
    username = subprocess.run(['pass', 'SplunkUN'], capture_output=True)
    username = username.stdout.decode('utf-8').split()
    print(username);
    password = subprocess.run(['pass', 'SplunkPW'], capture_output=True)
    password = password.stdout.decode('utf-8').split()
    r = requests.get(base_url + "/servicesNS/admin/search/auth/login",
                     data={'username': username, 'password': password}, verify=False)
    try:
        sk = minidom.parseString(r.text).getElementsByTagName('sessionKey')[0].firstChild.nodeValue
    except IndexError:
        pass
    try:
        print("Session Key:", sk)
    except UnboundLocalError:
        print('Username or password is incorrect.  Please run again')
        sys.exit(1)
    # copy_files()
    file_compare()
    file4 = open(similar_instances, 'r')
    lines = file4.readlines()
    line1 = []
    n = 1
    similar_len = len(d4)
    print(f'\n{similar_len} instances are common the past 3 weeks.  Checking Splunk for those datapoints.\n')
    for line in lines:
        line1 = line.split('\t')
        host = line1[0]
        print(host)
        print(f'Instance {n} of {similar_len}')
        # print('')
        # print(line1)
        # print('')
        ss = line1[1]
        #search_query = 'search=search index=ams_cq ' + 'host=' + host + ' source=*crx-quickstart/logs/error.log "*less than sizeDeltaEstimation*" OR "*Post cleanup size*" earliest=-3w@w latest=now'
        #r = requests.post(base_url + '/services/search/jobs/', data=search_query,
                          #headers={'Authorization': ('Splunk %s' % sk)},
                          #verify=False)
        done2 = False
        while not done2:
            print("Generating Splunk Search ID")
            try:
                search_query = 'search=search index=ams_cq ' + 'host=' + host + ' source=*crx-quickstart/logs/error.log "*less than sizeDeltaEstimation*" OR "*Post cleanup size*" earliest=-1w@w latest=now'
                r = requests.post(base_url + '/services/search/jobs/', data=search_query,
                                  headers={'Authorization': ('Splunk %s' % sk)},
                                  verify=False)
                sid = minidom.parseString(r.text).getElementsByTagName('sid')[0].firstChild.nodeValue
            except IndexError:
                pass
            sleep(5)
            print("Search ID is "+str(sid))
            print("Old Search ID is "+str(sidold))
            if sid != 0:
                if sid == sidold:
                    done2 = False
                else:
                    done2 = True
            else:
                done2 = False
        sidold = sid
        #print("Search ID", sid)
        done = False
        done = False
        while not done:
            r = requests.get(f'{base_url}/services/search/jobs/{sid}',
                             headers={'Authorization': ('Splunk %s' % sk)},
                             verify=False)
            response = minidom.parseString(r.text)
            for node in response.getElementsByTagName("s:key"):
                if node.hasAttribute("name") and node.getAttribute("name") == "dispatchState":
                    dispatchState = node.firstChild.nodeValue
                    print(dispatchState)
                    print("Search Status: ", dispatchState)
                    if dispatchState == "DONE":
                        done = True
                    else:
                        sleep(1)
        done1 = False
        while not done1:
            print("Generating Request")
            r = requests.get(f'{base_url}/services/search/jobs/{sid}/results/',
                             headers={'Authorization': ('Splunk %s' % sk)},
                             data={'output_mode': 'json'},
                             verify=False)
            sleep(5)
            print (r)
            rtest = json.loads(r.text)
            if rtest["messages"][0]["text"] == "call not properly authenticated":
                done1 = False
            else:
                done1 = True
        if rtest["results"] == []:
            print("Target Instance = " + host + " and its current Segment Store size is " + ss)
            print ("There are no Online TAR Compaction logs for the instance, hence please check the instance as to why it is NOT SPLUNKING the logs. Analysing the Offline Tar Compaction logs")
            otc_value = calculate_otc_stats(sk,host,ss)
            print()
            print("#" * 60 + 'Targeting next instance' + '#' * 60)
            print()
            calculate_baseline(host, ss, r, otc_value)
            continue
        else:
            calculate_baseline(host, ss, r)
        n += 1


def file_compare():
    with open(original, 'r') as file1:
        lines = file1.readlines()[1:]
        line1 = []
        d1 = {}
        for line in lines:
            line1 = line.replace('\n', '').split('\\t')
            d1[line1[0]] = line1[1]

    with open(file_2_path, 'r') as file2:
        lines = file2.readlines()[1:]
        line1 = []
        d2 = {}
        for line in lines:
            line1 = line.replace('\n', '').split('\\t')
            d2[line1[0]] = line1[1]

    with open(file_1_path, 'r') as file3:
        lines = file3.readlines()[1:]
        line1 = []
        d3 = {}
        for line in lines:
            line1 = line.replace('\n', '').split('\\t')
            d3[line1[0]] = line1[1]
    global d11, d22, d33
    d11 = {}
    d22 = {}
    d33 = {}
    for key in d1:
        if substring not in d1[key]:
            d11[key] = d1[key]
    for k in d11.copy():
        d11[k] = float(d11[k].strip('G'))
        if d11[k] < 20:
            del d11[k]
    for key in d2:
        if substring not in d2[key]:
            d22[key] = d2[key]
    for k in d22.copy():
        d22[k] = float(d22[k].strip('G'))
        if d22[k] < 20:
            del d22[k]
    for key in d3:
        if substring not in d3[key]:
            d33[key] = d3[key]
    for k in d33.copy():
        d33[k] = float(d33[k].strip('G'))
        if d33[k] < 20:
            del d33[k]
    # Compare 3 dictionaries for similar keys and add those items to d4
    global d4
    d4 = {}
    for k in d11.keys():
        if k in d22 and d33:
            d4[k] = d11[k]
    d4 = dict(sorted(d4.items()))
    file1.close()
    file2.close()
    file3.close()
    write_file(d4)


def write_file(dictionary):
    with open(similar_instances, 'w') as sf:
        for host in dictionary.copy():
            size = int(d4[host])
            sf.write(host + '\t' + str(size) + '\n')
    sf.close()


def copy_files():
    shutil.copyfile(file_2_path, file_1_path)
    print('Copied 2 --> 1')
    shutil.copyfile(file_3_path, file_2_path)
    print('Copied 3 --> 2')
    shutil.copyfile(original, file_3_path)
    print('Copied original --> 3')


def backup_files():
    shutil.copyfile(file_1_path, f'{file_1_path}.bak')
    print('Copied 1 --> 1.bak')
    shutil.copyfile(file_2_path, f'{file_2_path}.bak')
    print('Copied 2 --> 2.bak')
    shutil.copyfile(file_3_path, f'{file_3_path}.bak')
    print('Copied 3 --> 3.bak')


def email_send():
    outlook = app('Microsoft Outlook')

    msg = outlook.make(
        new=k.outgoing_message,
        with_properties={
            k.subject: f'AMS Basic - Segment Store Offenders - {email_date}',
            k.plain_text_content: f'Attached is this weeks offenders.'})
    msg.make(
        new=k.recipient,
        with_properties={
            k.email_address: {
                k.name: 'Tim Bonnett',
                k.address: 'bonnett@adobe.com'}})
    msg.make(
        new=k.recipient,
        with_properties={
            k.email_address: {
                k.name: 'Meet Kumar Jain',
                k.address: 'meejain@adobe.com'}})
    msg.make(
        new=k.recipient,
        with_properties={
            k.email_address: {
                k.name: 'Derek Wood',
                k.address: 'dwood@adobe.com'}})
    p = Alias(str(f'{cwd}/offenders_{date}.xlsx'))
    msg.make(
        new=k.attachment,
        with_properties={
            k.file: p})
    msg.open()
    msg.activate()


def calculate_baseline(hostname, segmentstore, response, *args):
    occurrence = 0
    skipgc = []
    postcleanup = []
    floatskipgc = []
    floatpostcleanup = []
    host_list = []
    r1 = json.loads(response.text)
    if r1["results"] == []:
        comments = "There are no Online TAR Compaction logs for the instance, hence please check the instance as to why it is NOT SPLUNKING the logs. You can however, further analyse the last Offline Compaction Logs"
    print()
    print("Target Instance = " + hostname + " and its current Segment Store size is " + segmentstore)
    for a in r1["results"]:
        print(a["_raw"])
        if "less than sizeDeltaEstimation" in a["_raw"]:
            if occurrence == 0:
                occurrence = + 1
                comments = "Skipping garbage collection is the latest log"
            indexlow1 = a["_raw"].find("to ")
            indexhigh1 = a["_raw"].find("GB (", indexlow1)
            indexlow1 += 3
            indexhigh1 + - 1
            value1 = a["_raw"][indexlow1:indexhigh1]
            # print ("skip",value1)
            skipgc.append(value1)
        elif ": cleanup completed" in a["_raw"]:
            if occurrence == 0:
                occurrence = + 1
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
            pass

    print("The baseline value analysis for " + hostname + " is as follows - ")
    floatskipgc = [float(x) for x in skipgc]
    floatpostcleanup = [float(x) for x in postcleanup]
    host_list.append(hostname)
    if r1["results"] == []:
        host_list.append(0)
        host_list.append(0)
        # host_list.append(0)
    try:
        print("The min. value after skipping garbage collection is " + str(min(floatskipgc)))
        print("The max. value after skipping garbage collection is " + str(max(floatskipgc)))
        host_list.append(min(floatskipgc))
        host_list.append(max(floatskipgc))
    except ValueError:
        print("skipping garbage collection logs doesn't exist for this instance")
        host_list.append(0)
        host_list.append(0)
    try:
        print("The min. value after Post Online Clean up size is " + str(min(floatpostcleanup)))
        print("The max. value after Post Online Clean up size is " + str(max(floatpostcleanup)))
        host_list.append(min(floatpostcleanup))
        host_list.append(max(floatpostcleanup))
    except ValueError:
        print("Post Online Clean up logs doesn't exist for this instance")
        host_list.append(0)
        host_list.append(0)
    print(comments)
    if "Skipping garbage collection" in comments:
        print("The latest log value is " + str(floatskipgc[0]))
        host_list.append(floatskipgc[0])
        host_list.append(0)
    elif "Post cleanup size" in comments:
        print("The latest log value is " + str(floatpostcleanup[0]))
        host_list.append(0)
        host_list.append(floatpostcleanup[0])
    offRC_value = ''.join(args)
    # print(offRC_value)
    if offRC_value == '':
        host_list.append('N/A')
    else:
        host_list.append(offRC_value)
    revised_segmentstore = float(segmentstore.replace('"', ''))
    host_list.append(revised_segmentstore)
    data_xslx.append(host_list)
    global df
    df = pd.DataFrame(
        data_xslx,
        columns=header
    )
    # df.sort_values(by='Current')
    print()
    print("#" * 60 + 'Targeting next instance' + '#' * 60)
    print()


def calculate_otc_stats(sk_otc,host_otc,ss_otc):
    sidold = 0
    sid = 0
    done2 = False
    while not done2:
        print("Generating Splunk Search ID")
        try:
            search_query = 'search=search index=ams_cq ' + 'host=' + host_otc + ' source=*crx-quickstart/logs/oak-tar-compact*.log "*after Compact*" earliest=-4mon@mon latest=now'
            r = requests.post(base_url + '/services/search/jobs/', data=search_query,
                              headers={'Authorization': ('Splunk %s' % sk_otc)},
                              verify=False)
            sid = minidom.parseString(r.text).getElementsByTagName('sid')[0].firstChild.nodeValue
        except IndexError:
            pass
        sleep(5)
        print("Search ID is " + str(sid))
        print("Old Search ID is " + str(sidold))
        if sid != 0:
            if sid == sidold:
                done2 = False
            else:
                done2 = True
        else:
            done2 = False
    sidold = sid
    # print("Search ID", sid)
    done = False
    while not done:
        r = requests.get(f'{base_url}/services/search/jobs/{sid}',
                         headers={'Authorization': ('Splunk %s' % sk_otc)},
                         verify=False)
        response = minidom.parseString(r.text)
        for node in response.getElementsByTagName("s:key"):
            if node.hasAttribute("name") and node.getAttribute("name") == "dispatchState":
                dispatchState = node.firstChild.nodeValue
                print("Search Status: ", dispatchState)
                if dispatchState == "DONE":
                    done = True
                else:
                    sleep(1)
    done1 = False
    while not done1:
        print("Generating Request")
        r = requests.get(f'{base_url}/services/search/jobs/{sid}/results/',
                         headers={'Authorization': ('Splunk %s' % sk_otc)},
                         data={'output_mode': 'json'},
                         verify=False)
        sleep(5)
        print(r)
        rtest = json.loads(r.text)
        if rtest["messages"][0]["text"] == "call not properly authenticated":
            done1 = False
        else:
            done1 = True
    if rtest["results"] == []:
        print(
            "There are no Offline Tar Compaction Logs for this instance as well. Please schedule OTC for this instance")
        print()
        return 0
    else:
        print (rtest["results"][0]["_raw"])
        indexhigh3 = rtest["results"][0]["_raw"].find("G")
        indexlow3 = rtest["results"][0]["_raw"].find(": ")
        indexlow3 += 2
        value3 = rtest["results"][0]["_raw"][indexlow3:indexhigh3]
        floatvalue3 = float(value3)
        print(f"As per the Offline Compaction Logs in last 4 months, the value after compaction is {floatvalue3}")
        return floatvalue3


def xlsx_create():
    writer = pd.ExcelWriter(f'{cwd}/offenders_{date}.xlsx', engine='xlsxwriter')
    result = df.sort_values(by='Current', ascending=False)
    result.to_excel(writer, sheet_name=f'offenders_{date}', index=False, na_rep='NaN')
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets[f'offenders_{date}'].set_column(col_idx, col_idx, column_width)
    # df.style.apply(highlight_rows, axis=1)
    writer.save()


def write_google_sheets():
    # scopes = ['https://www.googleapis.com/auth/spreadsheets',
    #           'https://www.googleapis.com/auth/drive']
    #
    # credentials = Credentials.from_service_account_file('~/.config/gspread/service_account.json', scopes=scopes)
    gc = gspread.service_account()
    sh = gc.open_by_key('16FEyh_Z7I9MqW13Nd0NVtBqmYuk9HsbWohwOu855SkQ')
    #
    # gauth = GoogleAuth()
    # drive = GoogleDrive(gauth)
    #
    # # open a google sheet
    # gs = gc.open_by_key('SS_Offenders')
    # # select a work sheet from its name
    # worksheet1 = gs.worksheet('SS_Offenders')
    worksheet = sh.get_worksheet(0)
    worksheet.clear()

    # write to dataframe
    set_with_dataframe(worksheet, df)
    format_with_dataframe(worksheet, df, include_column_header=True)


cwd = os.getcwd()
l1 = []
home = str(Path.home())
files_path = str(home + '/tmp/')
original = f'{home}/tmp/AMS-Basic-PROD-Instances-SegmentStoreSize-DiskSpaceUtilization.txt'
file_3_path = f'{cwd}/file3.txt'
file_1_path = f'{cwd}/file1.txt'
file_2_path = f'{cwd}/file2.txt'
file_4_path = f'{cwd}/file4.txt'
email_file_path = str(files_path + 'email_file.txt')
substring = 'M'
timing = {}
header_csv = ['Instance Name', 'Segment Store', 'Disk Space Utilization']
data = []
data_tmp = []
date = datetime.datetime.now()
date = date.strftime('%Y-%m-%d')
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
base_url = 'https://splunk-api.or1.adobe.net'
similar_instances = str(files_path + 'similar_instances.txt')
substring = 'M'
timing = {}
email_date = datetime.datetime.now()
email_date = email_date.strftime('%b %d, %Y')
header = [
    'hostname',
    'skipmin',
    'skipmax',
    'postmin',
    'postmax',
    'lastlogskip',
    'lastlogpost',
    'lastoffRclog',
    'current'
]
data_xslx = []

tmp_dir = os.path.isdir(files_path)
if tmp_dir:
    print('Directory exists.')
else:
    print('Creating directory...')
    os.mkdir(files_path)
    print(f'{files_path} created.  Proceeding.')
# backup_files()
original_gen()
res_data = []
for i in data:
    sub = i.split()
    res_data.append(sub)
res_data = res_data[1:]
# csv_create()
# team_email()
splunk()
# xlsx_create()
# email_send()
write_google_sheets()
print('Removing tmp files...')
for file in os.scandir(files_path):
    os.remove(file.path)
print('All finished.  See Excel sheet for review.')
