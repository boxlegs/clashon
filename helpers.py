import streamlit as st

from royaleutils.player import *
from royaleutils.clan import *

def refresh_button():
    if st.button("Refresh"):
        st.session_state.members = get_members(get_clan(CLAN_NAME)["tag"])