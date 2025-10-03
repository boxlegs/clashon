
from royaleutils.player import *
from royaleutils.clan import *
from helpers import refresh_button
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')

membernames = [player.player_name for player in st.session_state.members]

player_stats_page = st.set_page_config(
    page_title="Player Stats",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded",
    )
    
selection = st.selectbox('Select Player Name', options=membernames)
player = next((player for player in st.session_state.members if player.player_name == selection), None)
df = player.get_battlelog().to_dataframe(battle_types=["PvP", "trail"])

st.title(f"{player.player_name}'s Battle Log")
st.write(f"Battle log DF for {player.player_name} in clan {CLAN_NAME}")
st.write(df)

refresh_button()