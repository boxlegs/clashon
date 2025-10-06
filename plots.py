import plotly.express as px
import plotly.graph_objects as go
from royaleutils.clan import get_member_data
import pandas as pd
import concurrent.futures

def WinsVsLossesPlot(clan):
    df = pd.DataFrame(get_member_data(clan.clan_tag, get_details=True))

    # Calculate win ratio for each player
    df['win_ratio'] = df.apply(lambda row: row['wins'] / (row['wins'] + row['losses']) if (row['wins'] + row['losses']) > 0 else 0, axis=1)

    # Create scatter plot
    fig = px.scatter(
        df,
        x='losses',
        y='wins',
        color='name',
        text='name',
        size=[5]*len(df),
        size_max=15,
        color_discrete_sequence=px.colors.sequential.Viridis,
        hover_data={'win_ratio': ':.2f', 'wins': True, 'losses': True, 'name': True}
    )

    # Add x=y "Delete game" line
    min_val = min(df['losses'].min(), df['wins'].min())
    max_val = max(df['losses'].max(), df['wins'].max())
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(dash='dot', color='grey'),
        name='Delete game',
        showlegend=True
    ))
    fig.add_annotation(
        x=max_val, y=max_val,
        text='Delete game',
        showarrow=False,
        font=dict(color='grey', size=20),
        xanchor='right', yanchor='bottom',
        opacity=0.7
    )

    fig.update_traces(textposition='top center', textfont_size=18)
    fig.update_layout(
        title='Wins vs Losses per Player',
        xaxis_title='Losses',
        yaxis_title='Wins',
        legend_title='Player',
        height=600
    )

    return fig

def PowerRankingsPlot(members):
    # Convert Player objects into a DataFrame
    df = pd.DataFrame([{
        "name": m.name,
        "trophies": m.trophies,
        "total_games": m.total_games
    } for m in members])

    # Create scatter plot: trophies vs total_games
    fig = px.scatter(
        df,
        x="total_games",
        y="trophies",
        color="name",
        text="name",
        size=[5] * len(df),
        size_max=15,
        color_discrete_sequence=px.colors.sequential.Viridis,
        hover_data={"trophies": True, "total_games": True, "name": True}
    )

    fig.update_traces(textposition="top center", textfont_size=18)
    fig.update_layout(
        title="Trophies vs Total Games per Player",
        xaxis_title="Total Games",
        yaxis_title="Trophies",
        legend_title="Player",
        height=600
    )
    
    return fig


def _get_battle_df(member):
    
    battlelog = member.get_battlelog()
    df_battle = battlelog.to_dataframe(battle_types=["PvP"])
    if df_battle.empty:
        return None, member
    df_battle["Battle Time"] = pd.to_datetime(df_battle["Battle Time"], utc=True).dt.tz_convert('Australia/Brisbane')
    now_brisbane = pd.Timestamp.utcnow().tz_convert('Australia/Brisbane')
    df_battle = df_battle[df_battle["Battle Time"] >= now_brisbane - pd.Timedelta(hours=24)]
    if df_battle.empty:
        return None, member
    df_battle = df_battle.sort_values("Battle Time")
    # Add a datapoint of 0 5 minutes before the first point if it exists
    first_time = df_battle["Battle Time"].iloc[0] - pd.Timedelta(minutes=5)
    prepend = df_battle.iloc[[0]].copy()
    prepend["Battle Time"] = first_time
    prepend["accumTrophies"] = 0
    prepend["trophyChange"] = 0
    df_battle["accumTrophies"] = df_battle["trophyChange"].cumsum()
    df_battle = pd.concat([prepend, df_battle], ignore_index=True)
    return df_battle, member

def TrophyChangesPlot(members):
    fig = go.Figure()
    legend_entries = []

    # Use ThreadPoolExecutor to parallelize battlelog fetching and processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(_get_battle_df, members))

    for df_battle, member in results:
        if df_battle is None or df_battle.empty:
            continue
        total_gained = df_battle["trophyChange"].sum()
        fig.add_trace(go.Scatter(
            x=df_battle['Battle Time'],
            y=df_battle['accumTrophies'],
            mode='lines+markers',
            name=f"{member.name} (Δ{total_gained})",
            text=[f"{member.name} ({abs(total_gained)} trophies {'gained' if total_gained >= 0 else 'lost'})"] * len(df_battle),
            hoverinfo='text+x+y'
        ))
        legend_entries.append((total_gained, member.name, total_gained))

    fig.update_layout(
        title='Accumulated Trophy Change Over Time for All Members (last 24h)',
        xaxis_title='Battle Time (Brisbane)',
        yaxis_title='Accumulated Trophy Change',
        legend_title="Player",
        xaxis=dict(tickformat="%H:%M %a", tickangle=45),
        margin=dict(l=40, r=40, t=60, b=80),
        height=600,
        width=1000
    )
    
    return fig

def ThreeCrownLossesPlot(members):
    """
    Bar plot showing how many times each player has lost a battle (in their battlelog)
    where the opponent's crowns is 3.
    """
    player_names = []
    three_crown_losses = []

    for member in members:
        battlelog = member.get_battlelog()
        df_battle = battlelog.to_dataframe(battle_types=["PvP"])
        if df_battle.empty or "Opponent Crowns" not in df_battle.columns:
            player_names.append(member.name)
            three_crown_losses.append(0)
            continue
        df_battle["Battle Time"] = pd.to_datetime(df_battle["Battle Time"], utc=True).dt.tz_convert('Australia/Brisbane')
        now_brisbane = pd.Timestamp.utcnow().tz_convert('Australia/Brisbane')
        df_battle = df_battle[df_battle["Battle Time"] >= now_brisbane - pd.Timedelta(hours=24)]
        
        count = (df_battle["Opponent Crowns"] == 3).sum()
        player_names.append(member.name)
        three_crown_losses.append(count)

    fig = px.bar(
        x=player_names,
        y=three_crown_losses,
        labels={'x': 'Player', 'y': 'Three Crown Losses'},
        title='Number of Three Crown Losses per Player',
        text=three_crown_losses
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title='Player',
        yaxis_title='Three Crown Losses',
        height=500
    )
    return fig


def ElixirLeakedPlot(members):
    """
    Bar plot showing cumulative exilir leakage.
    """
    player_names = []
    elixir_leaked = []

    for member in members:
        battlelog = member.get_battlelog()
        df_battle = battlelog.to_dataframe(battle_types=["PvP"])
        if df_battle.empty or "Elixir Leaked" not in df_battle.columns:
            player_names.append(member.name)
            elixir_leaked.append(0)
            continue
        df_battle["Battle Time"] = pd.to_datetime(df_battle["Battle Time"], utc=True).dt.tz_convert('Australia/Brisbane')
        now_brisbane = pd.Timestamp.utcnow().tz_convert('Australia/Brisbane')
        df_battle = df_battle[df_battle["Battle Time"] >= now_brisbane - pd.Timedelta(hours=24)]
        
        count = df_battle["Elixir Leaked"].sum().round(2)
        player_names.append(member.name)
        elixir_leaked.append(count)

    fig = px.bar(
        x=player_names,
        y=elixir_leaked,
        labels={'x': 'Player', 'y': 'Elixir Leaked'},
        title='Amount of Elixir Leaked per Player',
        text=elixir_leaked
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title='Player',
        yaxis_title='Elixir Leaked',
        height=500
    )
    return fig


def MegaKnightLossesPlot(members):
    """
    Bar plot showing how many times each player lost to a deck containing Mega Knight
    in the last 24 hours.
    """
    player_names = []
    mega_knight_losses = []

    for member in members:
        battlelog = member.get_battlelog()
        df_battle = battlelog.to_dataframe(battle_types=["PvP"])
        if df_battle.empty:
            player_names.append(member.name)
            mega_knight_losses.append(0)
            continue

        df_battle["Battle Time"] = pd.to_datetime(df_battle["Battle Time"], utc=True).dt.tz_convert('Australia/Brisbane')
        now_brisbane = pd.Timestamp.utcnow().tz_convert('Australia/Brisbane')
        df_battle = df_battle[df_battle["Battle Time"] >= now_brisbane - pd.Timedelta(hours=24)]

        losses = 0
        for battle_data in battlelog.battles:  # iterate over raw battles
            battle_time = pd.to_datetime(battle_data.battle_time, utc=True).tz_convert('Australia/Brisbane')
            if battle_time < now_brisbane - pd.Timedelta(hours=24):
                continue

            if not battle_data.is_winner:  # player lost
                if any(card.name == "Mega Knight" for card in battle_data.opponent_cards):
                    losses += 1

        player_names.append(member.name)
        mega_knight_losses.append(losses)

    fig = px.bar(
        x=player_names,
        y=mega_knight_losses,
        labels={'x': 'Player', 'y': 'Losses to Mega Knight'},
        title='Losses to Mega Knight in Last 24 Hours',
        text=mega_knight_losses
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title='Player',
        yaxis_title='Losses',
        height=500
    )
    
    return fig


def LowerLevelOpponents(members):
    player_names = []
    losses_to_lower = []

    now_brisbane = pd.Timestamp.utcnow().tz_convert("Australia/Brisbane")

    for member in members:
        battlelog = member.get_battlelog()  # returns BattleLog
        battles = battlelog.get_battles()   # list of Battle/PvPBattle

        count = 0
        for b in battles:
            if b.type != "PvP":
                continue

            # Parse battle time into datetime
            battle_time = pd.to_datetime(b.battle_time, utc=True).tz_convert("Australia/Brisbane")
            if battle_time < now_brisbane - pd.Timedelta(hours=24):
                continue

            # Skip if no cards
            if not b.team_cards or not b.opponent_cards:
                continue

            team_avg = sum(c.max_level for c in b.team_cards) / len(b.team_cards)
            opp_avg = sum(c.max_level for c in b.opponent_cards) / len(b.opponent_cards)
            
            # Condition: player lost AND opponent had lower avg card level
            if b.opponent_crowns > b.team_crowns and opp_avg < team_avg:
                count += 1

        player_names.append(member.name)
        losses_to_lower.append(count)

    # Bar chart
    fig = px.bar(
        x=player_names,
        y=losses_to_lower,
        labels={"x": "Player", "y": "Losses to Lower-Level Opponents"},
        title="Losses vs Lower-Level Opponents (last 24h)",
        text=losses_to_lower
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Player",
        yaxis_title="Losses to Lower-Level Opponents",
        height=500
    )

    return fig

# TODO: # Trophies to games played
# TODO: # Games lost to opponents with lower level cards