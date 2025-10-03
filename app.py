
from royaleutils.player import *
from royaleutils.clan import *
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')


def setup():
    st.navigation({
        ""
    })

pages = [
    st.Page("pages/player_stats.py", icon="🏰", title="Player Stats"),
    st.Page("pages/clan_stats.py", icon="🏯", title="Clan Stats")
]

if "members" not in st.session_state:
    print("Not in session state")
    st.session_state.members = get_members(get_clan(CLAN_NAME)["tag"])

st.navigation(pages).run()

with st.sidebar.title("Clash On!"):
    st.sidebar.write("A Clash Royale stats dashboard")
    st.sidebar.write("Select a page from the navigation above.") 
       
