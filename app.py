
from royaleutils.player import *
from royaleutils.clan import *
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import plots
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')

logging.basicConfig(level=LOGGING_LEVEL)

# Start Loading plots
if "clan" not in st.session_state: 
    st.session_state.clan = Clan(CLAN_NAME)
    
pages = [
    st.Page("pages/clan_stats.py", icon="🏯", title="Clan Stats"),
    st.Page("pages/player_stats.py", icon="🏰", title="Player Stats")
]   

st.navigation(pages).run()

with st.sidebar.title("Clash On!"):
    st.sidebar.write("A Clash Royale stats dashboard")
    st.sidebar.write("Select a page from the navigation above.") 
       