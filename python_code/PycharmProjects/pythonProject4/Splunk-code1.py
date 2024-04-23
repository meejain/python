import splunklib.client as client
import splunklib.results as results

HOST = "splunk.or1.adobe.net"
PORT = 9997
USERNAME = "meejain"
PASSWORD = "wanderlusthnm@123456789"
SCHEME = "https"

service = client.connect(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    scheme=SCHEME)

print ("testing")

# Print installed apps to the console to verify login
for app in service.apps:
    print (app.name)



