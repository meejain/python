from appscript import app, k
import os
import openpyxl
from datetime import date
from pathlib import Path
import pyperclip as pc
import requests
from time import sleep
import datetime
import json
import subprocess
import sys
import maskpass

from pathlib import Path
from time import sleep

imsorg = []
customername = []
user = 'cae_rest'
pwd = 'Adobe@1234'
amstool = '/usr/local/bin/amstool'
home_dir = str(Path.home())
src = home_dir + '/Downloads/report.csv'
dst_folder = home_dir + '/Library/CloudStorage/OneDrive-Adobe/Quarterly_BPA_Analysis-Basic/Q3\'22-BestPracticesAnalyzer2.1.34/'






def getdatafromSNOW():
    print("Downloading data for Basic Customers from SNOW ...")
    url = 'https://adobedev.service-now.com/api/now/table/core_company?sysparm_query=u_active%3Dtrue%5Eu_product%3DAEM%20Basic%5Eu_status!%3DPre-Sale%5Eu_status!%3DNo%20deal%5Eu_status!%3DTerminated%5E&sysparm_display_value=true&sysparm_fields=name%2Cu_customer_success_engineer%2Cu_ims_org_id%2Cu_aem_forms%2Cu_end_date'
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
    # print(json_string)
    for i in data['result']:
        imsorg.append(i['u_ims_org_id'])
        customername.append(i['name'])
    print("SNOW data retrieved, proceeding further ... ")


def backup():
    for i in range(1,21):
        #customer = input('What is the Customer name ? ')
        instance = input(f'Enter the Prod Author instance name for the customer : ')
        subprocess.run([amstool, 'bba', instance, 'perform-backup', '-v', 'data', '-k', '30', 'Pre-BPA Package installation'])
        sleep(5)

def install():
    for j in range(1, 21):
        global password
        global ip
        instance_name = input('Enter the PROD Author instance name - ')
        z=instance_name.split("-")
        topology = z[0] + "-" + z[1]
        subprocess.run(
            [amstool, 'aem', instance_name, 'uploadinstall', 'best-practices-analyzer.all-2.1.34.zip'])
        sleep(30)
        subprocess.run([amstool, 'pw', topology, 'aempw'])
        #password = input('Enter the password')
        password = maskpass.askpass(prompt="Enter the password:", mask="ha")
        ls_lines = subprocess.check_output([amstool, 'list', instance_name])
        x = ls_lines.split()
        ip = x[2].decode()
        params = {
            'max-age': '0',
            'respond-async': 'true',
        }
        requests.get(f'https://{ip}/apps/best-practices-analyzer/analysis/report.json', verify=False, params=params,
                     auth=('admin', password))
        sleep(5)


def generatereport():
    for j in range(1, 21):
        global password
        global ip
        instance_name = input('Enter the PROD Author instance name - ')
        z=instance_name.split("-")
        topology = z[0] + "-" + z[1]
        subprocess.run([amstool, 'pw', topology, 'aempw'])
        #password = input('Enter the password')
        password = maskpass.askpass(prompt="Enter the password:", mask="ha")
        ls_lines = subprocess.check_output([amstool, 'list', instance_name])
        x = ls_lines.split()
        ip = x[2].decode()
        params = {
            'max-age': '0',
            'respond-async': 'true',
        }
        requests.get(f'https://{ip}/apps/best-practices-analyzer/analysis/report.json', verify=False, params=params,
                     auth=('admin', password))
        sleep(5)


def download():
    getdatafromSNOW()
    for z in range(1, 21):
        instance_name = input('Enter the PROD Author instance name - ')
        z = instance_name.split("-")
        topology = z[0] + "-" + z[1]
        subprocess.run([amstool, 'pw', topology, 'aempw'])
        password = maskpass.askpass(prompt="Enter the password:", mask="ha")
        # password = input('Enter the password')
        ls_lines = subprocess.check_output([amstool, 'list', instance_name])
        x = ls_lines.split()
        ip = x[2].decode()
        os.system(
            f'curl -k -u admin:\"{password}\" https://{ip}/apps/best-practices-analyzer/analysis/report.csv > ' + str(
                Path.home()) + '/Downloads/report.csv')
        sleep(5)
        # Please choose your local machine destination folder which is synced to One Drive BPA Reports folder accordingly and assign it to dst_folder variable below -
        dst_folder = home_dir + '/Library/CloudStorage/OneDrive-Adobe/Quarterly_BPA_Analysis-Basic/Q3\'22-BestPracticesAnalyzer2.1.34/'
        customer = input('What is the Customer name ? ')
        customer2 = customer.replace(' ', '')
        orgidindex = customername.index(customer)
        org_id = imsorg[orgidindex]
        dst = customer2 + '_' + org_id + '_BPA.csv'
        print(dst)
        try:
            if src:
                os.rename(src, dst_folder + dst)
        except FileNotFoundError:
            print('File doesnt exist.  Not moving report.')





def main():
    #subprocess.run([amstool, 'cache'])
    option = input(
        'Enter your choices accordingly - b for backups, i for BPA Package install & hitting the Generate Report button, g for Just hitting generate button & d for downloading the csv file into the folder: ')
    if option == 'b':
        backup()
    elif option == 'i':
        install()
    elif option == 'g':
        generatereport()
    elif option == 'd':
        download()




main()

#The below hits the Generate Report Button with a https warning message and start generating the BPA Report
#requests.get(f'https://{ip}/apps/best-practices-analyzer/analysis/report.json', verify=False, params=params, auth=('admin', password))

#The below will download the csv file
#os.system(f'curl -k -u admin:\"{password}\" https://{ip}/apps/best-practices-analyzer/analysis/report.csv > ' + str(Path.home()) + '/Downloads/report.csv')