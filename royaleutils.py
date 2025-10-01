import requests
import urllib
import pandas as pd
from dotenv import load_dotenv
import logging
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

headers = { "Authorization": f'Bearer {API_TOKEN}'}

def getclan(clan_name):
    clan_name = urllib.parse.quote(clan_name, safe='')
    return requests.get(f'https://api.clashroyale.com/v1/clans?name={clan_name}', headers = headers).json()["items"][0]

def getbattlelog(player_tag):
    player_tag = urllib.parse.quote(player_tag, safe='')
    data = requests.get(f'https://api.clashroyale.com/v1/players/{player_tag}/battlelog', headers = headers).json()

    team = data["team"]
    opponent = data["opponent"]
    
    return team,opponent,data

def getmembers(clan_tag):
    clan_tag = urllib.parse.quote(clan_tag, safe='')
    playerlist = requests.get(f'https://api.clashroyale.com/v1/clans/{clan_tag}/members', headers = headers).json()
    
    logging.info(f"Found {len(playerlist['items'])} members in clan {CLAN_NAME}")
    
    player_data = []

    for player in playerlist['items']:
        player_tag = urllib.parse.quote(player['tag'], safe='')
        player_data.append(requests.get(f'https://api.clashroyale.com/v1/players/{player_tag}', headers = headers).json())

    return player_data

        

