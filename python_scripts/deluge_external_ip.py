from deluge_client import DelugeRPCClient

# Replace these with your Deluge daemon's details
DELUGE_HOST = '192.168.2.78'
DELUGE_PORT = 58846
DELUGE_USERNAME = 'localclient'
DELUGE_PASSWORD = 'REDACTED'  # Set your Deluge daemon password here

client = DelugeRPCClient(DELUGE_HOST, DELUGE_PORT, DELUGE_USERNAME, DELUGE_PASSWORD)
client.connect()

if client.connected:
    external_ip = client.call('core.get_external_ip')
    print(f"{external_ip.decode('utf-8')}")
else:
    print("ERROR.")
