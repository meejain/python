#!/usr/bin/env python3

import os
import shutil


src = '/Users/meejain/Downloads/report.csv'
dst_folder = '/Users/meejain/OneDrive/Adobe/Tim Bonnett - BPA Reports/'
customer = input('What is the Customer name? ').replace(' ', '')
org_id = input('What is the Org ID? ')
dst = customer + '_' + org_id + '_BPA.csv'
# renamed_file = '/Users/dwood/Downloads/' + dst


# Rename file
os.rename(src, dst_folder + dst)
# Move file
# shutil.move(renamed_file, dst_folder + '/' + dst)
