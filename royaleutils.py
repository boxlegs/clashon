import requests
import urllib
import pandas as pd
from dotenv import load_dotenv
import logging
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

headers = { "Authorization": f'Bearer {API_TOKEN}'}

class Card(object):
    pass

# TODO: Support for parsing 2v2 battles
class Battle(object):
    def __init__(self, battle_data):
        self.type = battle_data["type"]
        self.battle_time = battle_data["battleTime"]
        
        # Parse team data
        team = battle_data["team"][0]
        
        self.team_tag = team["tag"]
        self.team_name = team["name"]
        self.team_crowns = team["crowns"]

        # Parse opponent data
        opponent = battle_data["opponent"][0]

        self.opponent_tag = opponent["tag"]
        self.opponent_name = opponent["name"]
        self.opponent_crowns = opponent["crowns"]
        self.player_tag = team["tag"]

        if self.type == "PvP":
            self.team_starting_trophies = team["startingTrophies"]
            self.team_trophy_change = team["trophyChange"]
            self.team_ending_trophies = team["startingTrophies"] + team["trophyChange"] 
            self.opponent_starting_trophies = opponent["startingTrophies"]
            self.opponent_trophy_change = opponent["trophyChange"]
            self.opponent_ending_trophies = opponent["startingTrophies"] + opponent["trophyChange"]

        self.is_winner = self.team_crowns > self.opponent_crowns
    
class BattleLog(object):
    def __init__(self, battles: list[dict]):
        self.battles = []
        for battle in battles: 
            self.battles.append(Battle(battle))
    
    def to_dataframe(self, battle_types: list[str] = None):
        """
        Dumps BattleLog to pandas DataFrame.
        """
        logging.info(f"Converting {len(self.battles)} battles to DataFrame")

        data = []
        for battle in self.battles:
            if not battle_types or battle.type in battle_types:
                logging.info("Adding battle to DataFrame")
                if battle.type == "PvP":
                    data.append({
                        "Battle Type": battle.type,
                        "Opponent Playertag": battle.opponent_tag,
                        "Opponent Name": battle.opponent_name,
                        "Opponent Crowns": battle.opponent_crowns,
                        "Opponent Starting Trophies": battle.opponent_starting_trophies,
                        "opponent_ending_trophies": battle.opponent_ending_trophies,
                        "player_tag": battle.team_tag,
                        "player_name": battle.team_name,
                        "player_crowns": battle.team_crowns,
                        "player_starting_trophies": battle.team_starting_trophies,
                        "player_ending_trophies": battle.team_ending_trophies,
                        "battle_time": battle.battle_time,
                        "is_winner": battle.is_winner
                    })
                else: # TODO: Non-PvP battles lack trophy attributes
                    continue
            else:
                logging.info(f"Skipping battle of type {battle.type}")
        return pd.DataFrame(data)

class Player(object):
    def __init__(self, player_data=None, player_tag=None):
        if not player_data and player_tag:
            player_data = get_player_data(player_tag)
        
        self.player_tag = player_data["tag"]
        self.battlelog = None

    def generate_battlelog(self):
        """
        Parse battle log from the /battlelog endpoint 
        """ 
        
        self.battlelog = BattleLog(get_battlelog_data(self.player_tag))

        return

    def get_battlelog(self):
        """
        Return BattleLog object
        """
        if not self.battlelog:
            self.generate_battlelog()
        return self.battlelog
    

def get_player_data(player_tag):
    player_tag = urllib.parse.quote(player_tag, safe='')
    return requests.get(f'https://api.clashroyale.com/v1/players/{player_tag}', headers = headers).json()


def get_clan(clan_name=CLAN_NAME):
    return requests.get(f'https://api.clashroyale.com/v1/clans?name={clan_name}', headers = headers).json()["items"][0]

def get_battlelog_data(player_tag):
    player_tag = urllib.parse.quote(player_tag, safe='')
    data = requests.get(f'https://api.clashroyale.com/v1/players/{player_tag}/battlelog', headers = headers).json()
    
    return data

def get_member_data(clan_tag):
    clan_tag = urllib.parse.quote(clan_tag, safe='')
    playerlist = requests.get(f'https://api.clashroyale.com/v1/clans/{clan_tag}/members', headers = headers).json()
    
    logging.info(f"Found {len(playerlist['items'])} members in clan {CLAN_NAME}")
    
    player_data = []

    for player in playerlist['items']:
        player_data.append(get_player_data(player['tag']))

    return player_data

def get_members(clan_tag):
    members = get_member_data(clan_tag)
    return (Player(player_data=member) for member in members)

# clan = getclan()
# members=getmembers(clan["tag"])
# df = pd.DataFrame(members)

