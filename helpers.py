import streamlit as st
import plots

from royaleutils.player import *
from royaleutils.clan import *

def refresh_button():
    if st.button("Refresh"):
        st.session_state.clear()
        
        # Start Loading plots
        if "clan" not in st.session_state: 
            st.session_state.clan = Clan(CLAN_NAME)