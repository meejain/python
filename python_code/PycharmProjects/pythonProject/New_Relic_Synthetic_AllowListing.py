import json
import requests
 
def preparing_entries_for_NR_SG():
    NR_SG_Entries = []
    NR_SYN_URL = 'https://s3.amazonaws.com/nr-synthetics-assets/nat-ip-dnsname/production/ip.json'
    with requests.get(NR_SYN_URL) as response:
        if response.status_code == 200:
            data = json.loads(response.text)
            for x in range(1, 6):
                print('Enter the Region ', x)
                REGION = str(input(""))
                for i in data[REGION]:
                    i = i + '/32'
                    NR_SG_Entries.append(i)
        else:
            print('An error occurred while attempting to retrieve data from NR')
    NR_SG_Entries = list(dict.fromkeys(NR_SG_Entries))
    print("Here is the list - ", '[%s]' % ', '.join(map(str, NR_SG_Entries)))
 
 
def main():
    preparing_entries_for_NR_SG()
 
main()
