
from royaleutils import *
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')

# clan = get_clan()
# members=get_members(clan["tag"])
player = Player(player_tag="#V8LVP0028")
df = player.get_battlelog().to_dataframe(battle_types=["PvP"])
df