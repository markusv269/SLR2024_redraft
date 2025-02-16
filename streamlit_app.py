import streamlit as st
import pandas as pd
# import pyarrow.parquet as pq
# import matplotlib.pyplot as plt
# import seaborn as sns
# import ast
import numpy as np

# --- Streamlit-Setup ---
st.set_page_config(page_title="SLR 2024 Dashboard", layout="wide")
tab1,tab2,tab3,tab4,tab5 = st.tabs(["🏠 Start", "📊 Matchups", "📅 Wochenkategorien", "📋 Roster", "👨‍👨‍👧‍👦 Users"])

# --- Daten laden mit Caching ---
@st.cache_data
def load_matchups():
    return pd.read_parquet('league_stats/matchups/matchups.parquet', engine='pyarrow')
def load_rosters():
    rosters = pd.read_parquet('league_stats/rosters/rosters.parquet', engine='pyarrow')
    rosters['starters'] = rosters['starters'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    rosters[['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'TE', 'FL', 'K', 'DEF']] = pd.DataFrame(rosters['starters'].to_list(), index=rosters.index)
    # metadata = rosters['metadata'].apply(pd.Series)
    settings = rosters['settings'].apply(pd.Series)
    # rosters = rosters.drop(columns=['metadata']).join(metadata)
    rosters = rosters.drop(columns=['settings']).join(settings)
    rosters['fpts'] = round(rosters['fpts'] + rosters['fpts_decimal'] / 100,2)
    rosters['fpts_against'] = round(rosters['fpts_against'] + rosters['fpts_against_decimal'] / 100,2)
    rosters['ppts'] = round(rosters['ppts'] + rosters['ppts_decimal'] / 100,2)
    rosters = rosters.drop(columns=['fpts_decimal', 'fpts_against_decimal', 'ppts_decimal'])
    return rosters
def load_users():
    users = pd.read_parquet('league_stats/users.parquet', engine='pyarrow')
    return users

matchups_df = load_matchups()
rosters_df = load_rosters()
users_df = load_users()

rosters_df = rosters_df.merge(users_df[['display_name', 'league_name', 'league_id', 'roster_id']], on=['league_id', 'roster_id'], how='left')


# --- Startseite ---
with tab1:
    st.title("Stoned Lack Redraft 2024 -- Wochenauswertung :football:")
    st.subheader("Wöchentlicher Überblick über die SLR 2024. 35 Ligen, 420 Manager, eine App.")
    st.write("Ankündigungen, Infos, Tipps auf dem Stoned Lack [Discord-Server](https://discord.gg/V9pt9MZ6Ch).")
    st.image("Pictures/SL_logo.png", width=150)

# --- Matchups ---
with tab2:
    st.title("Wöchentliche Matchups")

    # matches = matchups_df.groupby(['league_id', 'week', 'matchup_id'])
    
    # Unnötige Spalten entfernen und Spaltennamen umbenennen
    matchups_show = matchups_df[~matchups_df['matchup_id'].isin([0, None])]
    matchups_show = matchups_show.drop(columns=['custom_points', 'players_points'])
    matchups_show = matchups_show.rename(columns={
        'points': 'Punkte',
        'roster_id': 'Roster-ID',
        'matchup_id': 'Matchup-ID',
        'starters': 'Starter',
        'starters_points': 'Starter Punkte',
        'week': 'Woche',
        'league_id': 'League-ID'
    })

    # # Barplot für min, max und durchschnittliche Punkte pro Woche
    # st.subheader("📊 Punkteverteilung pro Woche")
    # stats_df = matchups_df[~matchups_df['matchup_id'].isin([0, None])].groupby("week")["points"].agg(["min", "mean", "max"]).reset_index()
    
    # fig, ax = plt.subplots(figsize=(10, 3))
    # sns.barplot(data=stats_df.melt(id_vars="week", var_name="Stat", value_name="Wert"), x="week", y="Wert", hue="Stat", ax=ax)
    # # ax.set_title("Minimal, Maximal und Durchschnittlich erzielte Punkte pro Woche")
    # ax.set_xlabel("Woche")
    # ax.set_ylabel("Punkte")
    # st.pyplot(fig)

    # Annahme: matchups_show ist bereits definiert
    columns = matchups_show.columns.tolist()
    columns.remove('players')

    selected_column1 = st.selectbox("Filtern nach...", columns)

    if selected_column1:
        unique_values1 = matchups_show[selected_column1].dropna().unique()
        selected_value1 = st.selectbox("Wert festlegen...", unique_values1)

        remaining_columns = [col for col in columns if col != selected_column1]
        
        if remaining_columns:
            selected_column2 = st.selectbox("Weiterer Filter...", remaining_columns, index=0)
            unique_values2 = matchups_show[selected_column2].dropna().unique()
            selected_value2 = st.selectbox("Weiterer Wert festlegen...", unique_values2)

            # Daten filtern
            filtered_df = matchups_show[
                (matchups_show[selected_column1] == selected_value1) & 
                (matchups_show[selected_column2] == selected_value2)
            ]
        else:
            filtered_df = matchups_show[matchups_show[selected_column1] == selected_value1]

    st.dataframe(filtered_df, hide_index=True)


# --- Wochenkategorien ---
with tab3:
    st.title("Wochenkategorien")
    
    if not matchups_df.empty:
        select_week = st.selectbox("Woche auswählen", sorted(matchups_df['week'].unique()), index=0)
        week_df = matchups_df[matchups_df['week'] == select_week]
        
        # Shootout der Woche
        st.subheader('🔥 Shootout der Woche')
        shootout_df = week_df.groupby(['league_id', 'matchup_id'])['points'].sum().reset_index()
        st.dataframe(shootout_df.sort_values(by='points', ascending=False).head(1), hide_index=True)
        
        # Klatsche der Woche
        st.subheader('💀 Klatsche der Woche')
        klatsche_df = week_df.groupby(['league_id', 'matchup_id'])['points'].agg(lambda x: x.max() - x.min()).reset_index()
        st.dataframe(klatsche_df.sort_values(by='points', ascending=False).head(1), hide_index=True)
        
        # Nailbiter der Woche
        st.subheader('😱 Nailbiter der Woche')
        st.dataframe(klatsche_df.sort_values(by='points', ascending=True).head(1), hide_index=True)
        
        # Top 5 Roster
        st.subheader('🏆 Top 5 Roster')
        top_roster_df = week_df[['points', 'league_id', 'starters']].sort_values(by='points', ascending=False).head(5)
        st.dataframe(top_roster_df, hide_index=True)
    else:
        st.warning("Keine Daten für die ausgewählte Woche verfügbar.")

with tab4:
    st.title("Roster")

    st.dataframe(rosters_df, hide_index=True)

with tab5:
    st.title('SLR Manager')

    # st.selectbox()
    user_show = users_df[['league_name', 'display_name', 'roster_id', 'draft_pos']]
    user_show = user_show.rename(columns={
        'league_name': 'Liga',
        'display_name': 'Manager',
        'roster_id': 'Roster-ID',
        'draft_pos': 'Draftposition'
    })
    selected_leagues = st.multiselect("Ligen auswählen:", user_show['Liga'].unique(), default=[])

    # Falls keine Liga ausgewählt ist, zeige den gesamten DataFrame
    filtered_df = user_show if not selected_leagues else user_show[user_show['Liga'].isin(selected_leagues)]

    # Dataframe anzeigen
    st.dataframe(filtered_df, hide_index=True)