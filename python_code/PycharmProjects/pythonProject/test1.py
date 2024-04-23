# Need to install requests package for python
# easy_install requests
import requests
import re
import json
import sys
import time
import collections
import pandas as pd
#import matplotlib.pyplot as plt

imsorg = []
customername = []
imsorgforms = []
customernameforms = []
nodata =[]
cscore = []
finalimsorgid = []
finalcustname = []

names=["eded","edfed","deqefd"]
age=[34,43,454]
loca=["delhi","meerut","harid"]
path=r'/Users/meejain/Downloads/file200.csv'
data={"nam es":names,"ages":age,"location":loca}
df=pd.DataFrame(data).to_csv(path)