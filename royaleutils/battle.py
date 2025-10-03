import pandas as pd
import logging,requests,urllib
from royaleutils.card import Card
from royaleutils.utils import call_api


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
        self.team_elixir_leaked = team.get("elixirLeaked", 0)
        
        # Parse opponent data
        opponent = battle_data["opponent"][0]

        self.opponent_tag = opponent["tag"]
        self.opponent_name = opponent["name"]
        self.opponent_crowns = opponent["crowns"]
        self.player_tag = team["tag"]
 
        self.is_winner = self.team_crowns > self.opponent_crowns
       
        self.team_cards = [Card(card_data) for card_data in team.get("cards", [])]
        self.opponent_cards = [Card(card_data) for card_data in opponent.get("cards", [])]
        
        logging.debug(self.team_cards)
        
    def dump(self):
        return {
                        "Battle Type": self.type,
                        "Opponent Playertag": self.opponent_tag,
                        "Team Name": self.team_name,
                        "Opponent Name": self.opponent_name,
                        "Opponent Crowns": self.opponent_crowns,
                        "Team Crowns": self.team_crowns,
                        "Team Player Tag": self.team_tag,
                        "Battle Time": self.battle_time,
                        "Is Winner": self.is_winner
                    }
    
class PvPBattle(Battle):
    
    def __init__(self, battle_data):
        super().__init__(battle_data)

        team = battle_data["team"][0]
        opponent = battle_data["opponent"][0]
        
        # PvP-specific attributes
        self.team_starting_trophies = team.get("startingTrophies", 0)
        self.team_trophy_change = team.get("trophyChange", 0) # Note trophyChange is absent when losing @ bottom of arena 
        self.team_ending_trophies = team.get("startingTrophies", 0) + team.get("trophyChange", 0)
        self.opponent_starting_trophies = opponent.get("startingTrophies", 0)
        self.opponent_trophy_change = opponent.get("trophyChange", 0)
        self.opponent_ending_trophies = opponent.get("startingTrophies", 0) + opponent.get("trophyChange", 0)
        
    def dump(self):
        """
        Dumps PvPBattle object to JSON.
        """
        return {
                        "Battle Type": self.type,
                        "Opponent Playertag": self.opponent_tag,
                        "Opponent Name": self.opponent_name,
                        "Opponent Crowns": self.opponent_crowns,
                        "Opponent Starting Trophies": self.opponent_starting_trophies,
                        "Opponent Ending Tropgies": self.opponent_ending_trophies,
                        "Team Player Tag": self.team_tag,
                        "Team Name": self.team_name,
                        "Team Crowns": self.team_crowns,
                        "Team Starting Trophies": self.team_starting_trophies,
                        "Team Ending Trophies": self.team_ending_trophies,
                        "Battle Time": self.battle_time,
                        "Is Winner": self.is_winner,
                        "trophyChange": self.team_trophy_change,
                        "Elixir Leaked": self.team_elixir_leaked,
                        "Team Cards": [card.name for card in self.team_cards],
                        "Opponent Cards": [card.name for card in self.team_cards]
                    }
        
class BattleLog(object):
    """
    Collection of player's previous battles.
    """
    
    def __init__(self, battles: list[dict]):
        self.battles = []
        for battle in battles:
            match (battle['type']):
                case "PvP":
                    self.battles.append(PvPBattle(battle))
                case "trail":
                    self.battles.append(PvPBattle(battle))
                case _:
                    logging.warning(f"No specific subclass for battle type \"{battle['type']}\". Using generic Battle class.")
                    self.battles.append(Battle(battle))
                        
    def get_battles(self) -> list[Battle]:
        """
        Return list of Battle objects.
        """
        return self.battles
    
    def to_dataframe(self, battle_types: list[str]|None = None) -> pd.DataFrame:
        """
        Dumps BattleLog to pandas DataFrame.
        """
        logging.info(f"Converting {len(self.battles)} battles to DataFrame")

        data = []
        for battle in self.battles:
            if not battle_types or battle.type in battle_types:
                data.append(battle.dump())
                        
        return pd.DataFrame(data)
    
def get_battlelog_data(player_tag):
    player_tag = urllib.parse.quote(player_tag, safe='')
    data = call_api(f'https://api.clashroyale.com/v1/players/{player_tag}/battlelog').json()
    
    return data