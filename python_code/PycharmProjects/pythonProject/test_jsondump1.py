import requests
import re
import json
import sys
import time
aws_region='useast'
new_data= {
            'nr_region': 'test',
            'nr_pl': 'no_prefix_list_assigned'
        }
with open('data.txt', 'a+') as file:
    file_data = json.load(file)
    file_data[f'{aws_region}'].append(new_data)
    file.seek(0)
    json.dump(file_data, file, indent=4)
