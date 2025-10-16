
from royaleutils.player import *
from royaleutils.clan import *
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import plots
from helpers import * 

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')

player_stats_page = st.set_page_config(
    page_title="Clan Stats",
    page_icon="🏯",
    layout="wide",
    initial_sidebar_state="expanded",
    )

st.image("https://etgeekera.com/wp-content/uploads/2016/05/clash-royale-banner.jpg", use_container_width=True)

if "clan" not in st.session_state: 
    st.session_state.clan = Clan(CLAN_NAME)

clan = st.session_state.clan
members = get_members(clan.clan_tag)

st.title(f"Clan Overview: {CLAN_NAME}")
st.markdown(f"**Clan Tag:** {clan.clan_tag}")
st.markdown(f"**Clan Score:** {clan.clan_score}")
st.markdown(f"**Clan Member Count:** {clan.clan_member_count}")

df = pd.DataFrame(clan.to_dataframe())
st.dataframe(df)

st.markdown(f"## Trophy Changes (Trophies < 10000, last 24h)")
st.plotly_chart(plots.TrophyChangesPlot(members, ["PvP"]), use_container_width=True)

st.markdown(f"## Trophy Changes (Trophies > 10000, last 24h)")
st.plotly_chart(plots.TrophyChangesPlot(members, ["trail"]), use_container_width=True)

st.markdown(f"## Historical Wins Vs Losses")
st.plotly_chart(plots.WinsVsLossesPlot(st.session_state.clan), use_container_width=True)

st.markdown(f"## Power Rankings")
st.plotly_chart(plots.PowerRankingsPlot(members), use_container_width=True)

st.markdown(f"## Three Crown Losses (last 24h\)")
st.plotly_chart(plots.ThreeCrownLossesPlot(members), use_container_width=True)

st.markdown(f"## Elixir Leaked (last 24h\)")
st.plotly_chart(plots.ElixirLeakedPlot(members), use_container_width=True)

st.markdown(f"## Battles Lost to Mega Knight (last 24h\)")
st.plotly_chart(plots.MegaKnightLossesPlot(members), use_container_width=True)

st.markdown(f"## Battles Lost to Opponents with Lower Level Cards")
st.plotly_chart(plots.LowerLevelOpponents(members), use_container_width=True)