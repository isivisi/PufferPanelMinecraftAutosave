# Auto save minecraft servers using PufferPanel 2 API

from dotenv import load_dotenv
import requests
import json
import subprocess
import time
import sys
import os

run_command = '/server/[id]/console'

load_dotenv()

api_endpoint = os.environ.get("API_ENDPOINT")
servers = json.loads(os.environ.get("SERVERS"))
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
api_token = os.environ.get("API_TOKEN")
save_interval = int(os.environ.get("SAVE_INTERVAL"))

print("Running autosave daemon")

while True:
    response = requests.post(
        api_endpoint + '/oauth2/token',
        data={
            'grant_type': 'client_credentials', 
            'client_id': client_id, 
            'client_secret': client_secret,
            'response_type': 'code'},
        auth=(client_id, client_secret),
    )

    access_token = response.json()["access_token"]

    def sendToConsole(server, command):
        requests.post(
            api_endpoint + '/daemon/server/' + server + '/console',
            data=command,
            headers= {
                "Authorization": "Bearer " + access_token,
                'Content-Type': "application/json",
                'Accept': "application/json"
            },
        )

    for server in servers:
        print("Running autosave on " + server)
        sendToConsole(server, 'say Saving world :)')
        sendToConsole(server, 'save-all')
    
    time.sleep(60 * save_interval)