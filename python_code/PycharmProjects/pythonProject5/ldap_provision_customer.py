#!/usr/bin/env python3

import json
import os
import subprocess
import sys

from pathlib import Path
from time import sleep
from tqdm import tqdm


def main():
    subprocess.run([amstool, 'cache'])
    topos(customer)
    # print(configured_ldap)
    # if 'False' in configured_ldap:
    #     print('Sleeping 7 min to allow bb action to occur...')
    #     for i in tqdm(range(14)):
    #         sleep(30)
    # else:
    #     print('No need to sleep all topologies are already configured for LDAP.  Proceeding.')
    user_info()
    delete_file(file)
    # Run AMSTool Cache
    subprocess.run([amstool, 'cache'])
    print('\nAll done')


def backup(topology):
    subprocess.run([amstool, 'bba', topology, 'perform-backup', '-v', 'root', '-k', '7', 'Pre-LDAP'])

def cmdline(command):
    process = subprocess.check_output(args=command, universal_newlines=True, shell=True)
    return process


def topos(c):
    cmd = subprocess.check_output(f'{amstool} list {customer} -d top | uniq', shell=True, text=True)

    for topo in cmd.split('\n'):
        topology.append(topo)
    topology.remove('')
    print(*topology, sep='\n')
    question = input('Does this list look correct (y/n)? ')
    if question == 'n':
        print("List isn't correct, try again.")
        exit(0)

    # Enable ldap for topologies in the list.  You need valid amstool auth basic and that token as a variable ims_token=
    for t in topology:
        print('~' * 50 + t + '~' * 50)
        tmp_bb_url = subprocess.run([amstool, 'info', t, 'bb'], capture_output=True)
        bb_url_list = tmp_bb_url.stdout.decode("utf-8")
        for item in bb_url_list.split('\n'):
            if "Actions:" in item:
                bb_url_line = item.strip()
                bb_url_line = bb_url_line.split(' ')
                bb_url = bb_url_line[-1]

        try:
            print(bb_url)
        except:
            print('Big Bear URL not found.  Exiting.')
            sys.exit(0)
        # print(type(bb_url))
        # find out if ldap is needed
        tmp_ldap_active = subprocess.run([amstool, 'list', t, '-d', 'amsLDAP'], capture_output=True)
        ldap_active = tmp_ldap_active.stdout.decode('utf-8')
        ldap_active = ldap_active.split('\n')
        ldap_active = ldap_active[0]
        configured_ldap.append(ldap_active)
        if ldap_active == 'False':
            print('Topo not configured for ldap.  Taking backups of the root volume.')
            backup(t)
            print('Sleeping 5 min for backups to run.')
            for i in tqdm(range(10)):
                sleep(30)
            # tmp_curl_command = subprocess.Popen(['curl', '-D', '-', '-X', 'POST', '-d', """'{ "actionId": "configure-instance-ldap", "parameters": { }}'""", '-H', 'Accept: application/json', bb_url, '-H', f"Authorization: Bearer {token}"], stdout=subprocess.PIPE)
            # bb_action = tmp_curl_command.stdout.read()
            print('Running Big Bear action to configure ldap...')
            cmd1 = f'curl -D - -X POST -d \'{{ "actionId": "configure-instance-ldap", "parameters": {{ }}}}\' -H "Accept: application/json" {bb_url} -H "Authorization: Bearer {token}"'
            # print(cmdline(cmd1))
            # p = subprocess.Popen(['curl', '-D', '-', '-X', 'POST', '-d', '{ "actionId": "configure-instance-ldap", "parameters": { }}', '-H', "'Accept: application/json'", bb_url, '-H', '"Authorization: Bearer', token + '"'), stdout = subprocess.PIPE]
            # for item in cmdline(cmd1):
            #     if '"tokenID" :' in item:
            #         bb_action_token = item.strip()
            #         bb_action_token = bb_action_token.split(': ')
            #         bb_action_token = bb_action_token[-1]
            #         global bb_action_token
            bb_action = cmdline(cmd1)
            bb_action = bb_action.split('\n')
            # print(len(bb_action))
            # print(bb_action)
            # if '"tokenID" :' in bb_action:
            # bb_action_index = bb_action.index(15)
            bb_action_token = bb_action[6]
            bb_action_token = bb_action_token.split(': ')
            bb_action_token = bb_action_token[-1]
            bb_action_token = bb_action_token.replace('http', 'https')
            bb_action_token = bb_action_token.rstrip()
                # bb_action_token = bb_action_token.split(': ')
                # bb_action_token = bb_action_token[-1]
            # bb_action_token = bb_action.split('n')
            bb_action_location = bb_url + '/' + bb_action_token
            while True:
                cmd2 = f'curl {bb_action_token} | grep state'
                print(cmd2)
                if "running" in cmdline(cmd2):
                    print('Big Bear action still running...')
                    sleep(30)
                elif "error" in cmdline(cmd2):
                    print('Big Bear action failed.  Investigate the reason why.')
                    exit(1)
                else:
                    print('\nBig Bear action all finished!')
                    break
            # sleep(420)
        else:
            print('Topo is already configured for ldap.  Skipping step.')

        # except UnboundLocalError:
        #     print("Big Bear not called skipping sleep")
        #     pass


def user_info():
    # Creates a dictionary of Users and their associated keys
    users_dict = {}
    add_user = input('Do you want to add a user/key? (y/n) ').lower()
    if add_user == 'y':
        while True:
            user = ''
            key = ''
            user = input('What is the username you want to add? ')
            if user == '':
                print('Username cannot be blank.  Try again or enter "n".')
                continue
            key = input('What is the SSH Key for this user? ')
            if key == '':
                print('The SSH key cannot be blank.  Try username/key combo again or enter "n".')
                continue
            users.append({'username': user, 'ssh_key': key})
            advance = input('Do you want to add another? (y/n)  ').lower()
            if advance == 'y':
                continue
            elif advance == 'n':
                break
        for user in users:
            users_dict[user["username"]] = user["ssh_key"]
        # Write to a json file to have the usernames and keys in a list of dictionaries
        with open(home + f'/customer_keys_{customer}.json', 'w') as outfile:
            json.dump(users_dict, outfile)
        provision(file)
    elif add_user == 'n':
        print('No user to add here.')
    else:
        print('Please enter either y/n.  Starting list over.')
        user_info()


def provision(f):
    # Provision customers for ssh with their keys in all the topologies listed in the Topology list
    for i in topology:
        print('~' * 50)
        print(i)
        for u in users:
            print('~' * 50)
            print('Adding ' + u['username'] + '...')
            subprocess.run([amstool, 'bba', i, 'provisionssh', '-f', f, '-w'])
            print('Added ' + u['username'])
            print('~' * 50)
    print('~' * 50)
    print()


def delete_file(f):
    # Delete customer_keys.json created (if exists)
    if os.path.exists(file):
        os.remove(file)
        print("The file has been deleted successfully")
    else:
        print("The file does not exist!")


home = str(Path.home())
topology = []
users = [
]
configured_ldap = []

tmp_amstool = subprocess.run(['which', 'amstool'], capture_output=True)
amstool = tmp_amstool.stdout.decode("utf-8")
amstool = amstool.strip('\n')
# print(amstool)
if amstool == '':
    amstool = f'{home}/Library/Python/3.9/bin/amstool'
customer = input("What does the topologies start with? ")
tmp_token = subprocess.run([amstool, 'auth', 'basic', '-e'], capture_output=True)
token = tmp_token.stdout.decode('utf-8')
token = token.strip()
# print(token)
file = home + f'/customer_keys_{customer}.json'

main()



#
#
#
#

