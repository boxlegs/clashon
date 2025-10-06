from royaleutils.utils import * 
from royaleutils.battle import *
import pandas as pd
import logging,requests,urllib

class Player(object):
    def __init__(self, player_data=None, player_tag=None):
        if not player_data and player_tag:
            player_data = get_player_data(player_tag)
        
        self.tag = player_data["tag"]
        self.name = player_data["name"]
        self.arena = player_data["arena"]["name"]
        self.trophies = player_data["trophies"]
        self.total_games = player_data["battleCount"]
        self.wins = player_data["wins"]
        self.losses = player_data["losses"]
        self.three_crown_wins = player_data["threeCrownWins"]
        self.favourite_card = player_data.get("currentFavouriteCard", None)
        self.battlelog = None
        self.role = player_data["role"]
        self.donations = player_data["donations"]
        self.donations_received = player_data["donationsReceived"]
        

    def generate_battlelog(self):
        """
        Parse battle log from the /battlelog endpoint 
        """ 
        self.battlelog = BattleLog(get_battlelog_data(self.tag))
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
    return call_api(f'https://api.clashroyale.com/v1/players/{player_tag}').json()
