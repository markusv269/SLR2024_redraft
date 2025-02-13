import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import matplotlib.pyplot as plt
import seaborn as sns

# --- Streamlit-Setup ---
st.set_page_config(page_title="SLR 2024 Dashboard", layout="wide")
st.image("Pictures/SL_logo.png", width=150)

# --- Daten laden mit Caching ---
@st.cache_data
def load_matchups():
    return pd.read_parquet('league_stats/matchups/matchups.parquet', engine='pyarrow')

matchups_df = load_matchups()

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
menu_option = st.sidebar.selectbox("Wähle eine Seite:", ["🏠 Start", "📊 Matchups", "📅 Wochenkategorien"])

# --- Startseite ---
if menu_option == "🏠 Start":
    st.title("Stoned Lack Redraft 2024 -- Wochenauswertung :football:")
    st.subheader("Wöchentlicher Überblick über die SLR 2024. 35 Ligen, 420 Manager, eine App.")
    st.write("Ankündigungen, Infos, Tipps auf dem Stoned Lack [Discord-Server](https://discord.gg/V9pt9MZ6Ch).")

# --- Matchups ---
elif menu_option == "📊 Matchups":
    st.title("Wöchentliche Matchups")
    
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

    # Barplot für min, max und durchschnittliche Punkte pro Woche
    st.subheader("📊 Punkteverteilung pro Woche")
    stats_df = matchups_df.groupby("week")["points"].agg(["min", "mean", "max"]).reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=stats_df.melt(id_vars="week", var_name="Stat", value_name="Wert"), x="week", y="Wert", hue="Stat", ax=ax)
    # ax.set_title("Minimal, Maximal und Durchschnittlich erzielte Punkte pro Woche")
    ax.set_xlabel("Woche")
    ax.set_ylabel("Punkte")
    st.pyplot(fig)

    # Filteroptionen
    columns = matchups_show.columns.tolist()
    selected_column = st.selectbox("Filtern nach...", columns)
    unique_values = matchups_show[selected_column].unique()
    selected_value = st.selectbox("Wert festlegen...", unique_values)
    
    # Gefilterte Daten anzeigen
    filtered_df = matchups_show[matchups_show[selected_column] == selected_value]
    st.dataframe(filtered_df, hide_index=True)

# --- Wochenkategorien ---
elif menu_option == "📅 Wochenkategorien":
    st.title("Wochenkategorien")
    
    if not matchups_df.empty:
        select_week = st.selectbox("Woche auswählen", sorted(matchups_df['week'].unique(), reverse=True), index=0)
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
