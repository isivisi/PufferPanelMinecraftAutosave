# Auto save minecraft servers using PufferPanel 2 API

from dotenv import load_dotenv
import requests
import json
import subprocess
import re
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

serverPlayerStatus = {} # if server should be saved on next tick
for server in servers: serverPlayerStatus[server] = {'shouldSave': False, 'lastUserLog': None}

def getAccessToken():
    response = requests.post(
        api_endpoint + '/oauth2/token',
        data={
            'grant_type': 'client_credentials', 
            'client_id': client_id, 
            'client_secret': client_secret,
            'response_type': 'code'},
            auth=(client_id, client_secret),
    )
    return response.json()["access_token"]

def sendToConsole(server, command):
    requests.post(
        api_endpoint + '/daemon/server/' + server + '/console',
        data=command,
        headers= {
            "Authorization": "Bearer " + getAccessToken(),
            'Content-Type': "application/json",
            'Accept': "application/json"
        },
    )

def getServerLogs(server):
    response = requests.get(
        api_endpoint + '/daemon/server/' + server + '/console',
        headers= {
            "Authorization": "Bearer " + getAccessToken(),
            'Content-Type': "application/json",
            'Accept': "application/json"
        },
    )
    return response.json()['logs'].split('\n')

def serverRunning(server):
    response = requests.get(
        api_endpoint + '/daemon/server/' + server + '/status',
        headers= {
            "Authorization": "Bearer " + getAccessToken(),
            'Content-Type': "application/json",
            'Accept': "application/json"
        },
    )
    return bool(response.json()['running'])


lastSaveTime = 0

while True: # 1 second tick

    for server in servers:
        logs = getServerLogs(server)
        for log in reversed(logs):
            if 'logged in with entity id' in log:
                if (serverPlayerStatus[server]['lastUserLog'] != log):
                    print('Detected player join, marking ' + server + 'to save on next interval')
                    serverPlayerStatus[server]['shouldSave'] = True
                    serverPlayerStatus[server]['lastUserLog'] = log

    curTime = int(time.time())

    if (curTime - lastSaveTime > (60 * save_interval)): # save interval tick
        lastSaveTime = curTime
        
        for server in servers:
            if serverPlayerStatus[server]['shouldSave']: # if we detected a player was online since last tick
                print("Players detected since last save, running autosave on " + server)
                sendToConsole(server, 'say Players detected, saving world :)')
                sendToConsole(server, 'save-all')
                serverPlayerStatus[server]['shouldSave'] = False
        
    #time.sleep(60 * save_interval)
    time.sleep(1)