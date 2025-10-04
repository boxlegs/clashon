
from royaleutils.player import *
from royaleutils.clan import *
from helpers import refresh_button
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title="Player Stats",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded",
    )

st.image("https://etgeekera.com/wp-content/uploads/2016/05/clash-royale-banner.jpg", use_container_width=True)

clan = st.session_state.clan

members = get_members(clan.clan_tag)

membernames = [player.name for player in members]

    
selection = st.selectbox('Select Player Name', options=membernames)
player = next((player for player in members if player.name == selection), None)
df = player.get_battlelog().to_dataframe(battle_types=["PvP", "trail"])

st.title(f"{player.name}'s Battle Log")
st.write(f"Battle log DF for {player.name} in clan {CLAN_NAME}")
st.write(df)

# refresh_button()