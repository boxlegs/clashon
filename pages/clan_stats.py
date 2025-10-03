
from royaleutils.player import *
from royaleutils.clan import *
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')

player_stats_page = st.set_page_config(
    page_title="Clan Stats",
    page_icon="🏯",
    layout="wide",
    initial_sidebar_state="expanded",
    )


clan = Clan(CLAN_NAME)
    
st.title(f"Clan Overview: {CLAN_NAME}")
st.markdown(f"**Clan Tag:** {clan.clan_tag}")
st.markdown(f"**Clan Score:** {clan.clan_score}")
st.markdown(f"**Clan Member Count:** {clan.clan_member_count}")

df = pd.DataFrame(get_member_data(clan.clan_tag))
df.drop(columns=['tag', 'lastSeen'])