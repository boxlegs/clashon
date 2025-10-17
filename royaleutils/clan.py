import pandas as pd
from dotenv import load_dotenv
from royaleutils.player import *
from royaleutils.utils import call_api
import logging
import os
import concurrent.futures

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')

headers = { "Authorization": f'Bearer {API_TOKEN}'}


class Clan(object):
    def __init__(self, clan_name=CLAN_NAME):
        clan_data = get_clan(clan_name)
        self.clan_name = clan_data['name']
        self.clan_tag = clan_data['tag']
        self.clan_score = clan_data['clanScore']
        self.clan_badge_id = clan_data['badgeId']
        self.clan_type = clan_data['type']
        self.clan_member_count = clan_data['members']
        self.clan_required_trophies = clan_data['requiredTrophies']
        self.clan_donations_per_week = clan_data['donationsPerWeek']
        self.clan_clan_war_trophies = clan_data['clanWarTrophies']
        self.clan_location = clan_data['location']['name'] if 'location' in clan_data else "Unknown"

        self.members = get_members(self.clan_tag)
    
    
    def to_dataframe(self):
        member_data = []
        for member in self.members:
            member_data.append({
                "Name": member.name,
                "Tag": member.tag,
                "Trophies": member.trophies,
                "Role": member.role,
                "Arena": member.arena,
                "Donations": member.donations,
                "Donations Received": member.donations_received
            })
        return pd.DataFrame(member_data)

def get_clan(clan_name=CLAN_NAME):
    return call_api(f'clans?name={clan_name}')["items"][0]


def get_member_data(clan_tag, get_details=False):
    clan_tag = urllib.parse.quote(clan_tag, safe='')
    playerlist = call_api(f'clans/{clan_tag}/members')
    
    logging.info(f"Found {len(playerlist['items'])} members in clan {CLAN_NAME}")
    
    player_data = []

    if get_details:
        # Parallelize get_player_data for each player using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            player_data = list(executor.map(lambda player: get_player_data(player['tag']), playerlist['items']))
        return player_data

    return playerlist['items']

def get_members(clan_tag):
    members = get_member_data(clan_tag, get_details=True)
    return [Player(player_data=member) for member in members]
