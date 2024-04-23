#!/usr/bin/env python3

from appscript import app, k
import os
import openpyxl
from datetime import date
from pathlib import Path
import pyperclip as pc
import requests
from time import sleep
import datetime



src = '/Users/meejain/Downloads/report.csv'
dst_folder = '/Users/meejain/OneDrive/Adobe/Tim Bonnett - BPA Reports/'
customer = input('What is the Customer name?\n')
customer2 = customer.replace(' ', '')
org_id = input('What is the Org ID?\n')
dst = customer2 + '_' + org_id + '_BPA.csv'

ip = input('Enter the IP of the author:\n')
password = input('Enter cq-admin-password:\n')

params = {
    'max-age': '0',
    'respond-async': 'true',
}

outlook = app('Microsoft Outlook')

msg = outlook.make(
    new=k.outgoing_message,
    with_properties={
        k.subject: 'AMS Basic - BPA Report - ' + customer,
        k.plain_text_content: 'Report starting'})
msg.make(
    new=k.recipient,
    with_properties={
        k.email_address: {
            k.address: 'ManServ-CEA@adobe.com'}})
msg.open()
msg.activate()
sleep(10)

# Generate a BPA report
requests.get(f'https://{ip}/apps/best-practices-analyzer/analysis/report.json', verify=False, params=params, auth=('admin', password))
current = datetime.datetime.now()
print ("Current time stamp:", str(current))
print('Generating BPA report.  Waiting 30 min.')
sleep(1800)
# Download csv file into Downloads
os.system(f'curl -k -u admin:\"{password}\" https://{ip}/apps/best-practices-analyzer/analysis/report.csv > ' + str(Path.home()) + '/Downloads/report.csv')
sleep(60)

# Rename and move file
try:
    if src:
        os.rename(src, dst_folder + dst)
except FileNotFoundError:
    print('File doesnt exist.  Not moving report.')

today = date.today()
today = today.strftime('%m/%d/%Y')
pc.copy(today)
print(f"Today's date is copied to the clip board. Please check off the {customer} in the spreadsheet.")
