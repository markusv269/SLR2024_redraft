import streamlit as st
from modules.matchups import get_matchups
import pandas as pd
import pyarrow.parquet as pq

st.logo("Pictures/SL_logo.png", link=None, size='large')

# st.dataframe(matchups_show, hide_index=True)
# print(max_week)

st.sidebar.title("Navigation")
menu_option = st.sidebar.selectbox("Wähle eine Seite:", ["Start", "Matchups", "Wochenkategorien"])

if menu_option == "🏠 Start":
    st.title("Stoned Lack Redraft 2024 -- Wochenauswertung :football:")
    st.subheader("Wöchentlicher Überblick über die SLR 2024. 35 Ligen, 420 Manager, eine App.")
    st.write("Ankündigungen, Infos, Tipps auf dem Stoned Lack [Discord-Server](https://discord.gg/V9pt9MZ6Ch).")

elif menu_option == "📊 Matchups":
    st.title("Wöchentliche Matchups")

    # matchups_pq = pq.read_table('league_stats/matchups/matchups.parquet')

    matchups_df = pd.read_parquet('league_stats/matchups/matchups.parquet', engine='pyarrow')
    # max_week = max(matchups_df['week'].unique())
    matchups_show = matchups_df[~matchups_df['matchup_id'].isin([0, None])].drop(columns=['custom_points', 'players_points'])
    matchups_show.columns = ['Punkte', 'Roster', 'Roster-ID', 'Matchup-ID', 'Starter', 'Starter Punkte', 'Woche', 'League-ID']

    columns = matchups_show.columns.tolist()
    selected_column = st.selectbox("Filtern nach...", columns)
    unique_values = matchups_show[selected_column].unique()
    selected_value = st.selectbox("Wert festlegen...", unique_values)

    filtered_df = matchups_show[matchups_show[selected_column] == selected_value]
    st.dataframe(filtered_df,hide_index=True)

elif menu_option == "Wochenkategorien":
    week_df = pd.read_parquet('league_stats/matchups/matchups.parquet', engine='pyarrow')
    select_week = st.selectbox("Woche auswählen", week_df['week'].unique())

    week_df = week_df[week_df['week'] == select_week]

    st.subheader('Shootout der Woche')
    if select_week != None:
        shootout_df = week_df.groupby(['league_id', 'matchup_id']).sum('points').reset_index()
        st.dataframe(shootout_df.sort_values(by='points', ascending=False).head(1),hide_index=True)

    st.subheader('Klatsche der Woche')
    if select_week != None:
        klatsche_df = week_df.groupby(['league_id', 'matchup_id'])['points'].agg(lambda x: x.max() - x.min()).reset_index()
        st.dataframe(klatsche_df.sort_values(by='points', ascending=False).head(1),hide_index=True)
    
    st.subheader('Nailbiter der Woche')
    if select_week != None:
        st.dataframe(klatsche_df.sort_values(by='points', ascending=True).head(1),hide_index=True)
    
    st.subheader('Top 5 Roster')
    if select_week != None:
        st.dataframe(week_df[['points', 'league_id', 'starters']].sort_values(by='points', ascending=False).head(5),hide_index=True)

    # # Beispiel-Datenframe
    # df = pd.DataFrame({
    #     'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    #     'Alter': [25, 30, 35, 40],
    #     'Stadt': ['Berlin', 'München', 'Hamburg', 'Berlin']
    # })

    # st.title("Dynamische Filter für DataFrame")

    # # Session-State für Filter
    # if "filters" not in st.session_state:
    #     st.session_state.filters = []

    # # Funktion zur Anwendung der Filter
    # def apply_filters(df, filters):
    #     for f in filters:
    #         column, value = f
    #         df = df[df[column] == value]  # Hier kannst du weitere Bedingungen anpassen
    #     return df

    # # Filter-Container
    # with st.expander("Filteroptionen"):
    #     # Auswahl der Spalte
    #     column = st.selectbox("Spalte wählen", df.columns, key="column_select")

    #     # Passende Filteroption je nach Datentyp
    #     if df[column].dtype == 'O':  # Objekt (String)
    #         value = st.selectbox("Wert wählen", df[column].unique(), key="value_select")
    #     else:  # Numerisch
    #         value = st.slider("Wert wählen", int(df[column].min()), int(df[column].max()), key="value_slider")

    #     # Filter hinzufügen
    #     if st.button("Filter hinzufügen"):
    #         st.session_state.filters.append((column, value))

    # # Gefiltertes DataFrame anzeigen
    # filtered_df = apply_filters(df, st.session_state.filters)
    # st.write(filtered_df)

    # # Möglichkeit, alle Filter zurückzusetzen
    # if st.button("Alle Filter zurücksetzen"):
    #     st.session_state.filters = []
    #     st.experimental_rerun()
