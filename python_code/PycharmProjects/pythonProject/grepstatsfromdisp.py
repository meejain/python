from appscript import app, k
import os
from datetime import date
from pathlib import Path
import requests
from time import sleep
import datetime
import json
import subprocess
import sys

from pathlib import Path
from time import sleep

imsorg = []
final3 = []
substr1 = "adobe";
customername = []
amstool = '/usr/local/bin/amstool'
home_dir = str(Path.home())


def getdatafromdispatchers(instance,customer):
    f = open("urls.txt", "w")
    subprocess.run([amstool, 'cmd', instance, 'sudo grep ServerAlias /etc/httpd/conf.d/enabled_vhosts/* | grep -v author | grep -v health | grep -v flush'], stdout=f);
    os.system("sort urls.txt | uniq | grep -v INFO > urls1.txt");
    fr = open('urls1.txt', 'r');
    filesize = (len(fr.readlines()));
    print(customer.replace("_", " ")+"#"+instance);
    if (filesize > 0):
        o = open('urls1.txt', 'r');
        for line in o:
            final1 = line.split('ServerAlias');
            lastentry = final1[len(final1)-1].strip();
            final2 = lastentry.split(' ');
            final3.extend(final2);
        for x in final3:
            if (len(x) > 1):
                if (substr1 not in x):
                    # if (substr2 not in x):
                        print("##"+x);
        final3.clear();
    # else:
    #     print("##Required data is not there");



def main():
    # row = 'Zeppelin_Gmbh_(Enterprise)#zeppelin-prod-65-dispatcher1eucentral1v2';
    # customerInfo = row.split('#');
    # instance = customerInfo[1];
    # customer = customerInfo[0];
    # getdatafromdispatchers(instance, customer);
    inputfile = open('newlist.txt', 'r');
    for line in inputfile:
        row = str(line);
        customerInfo = row.split('#');
        instance = customerInfo[1].strip();
        customer = customerInfo[0].strip();
        getdatafromdispatchers(instance,customer);


main();