import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st
import graphviz
import json
import requests

# --- Streamlit-Setup ---
st.set_page_config(page_title="SLR 2024 Dashboard", layout="wide")
tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs(["🏠 Start", "📊 Matchups", "📅 Wochenkategorien", "📋 Statistiken", "👨‍👨‍👧‍👦 Users", "NFL Player", "SLR Ligen"])

# --- Daten laden mit Caching ---
@st.cache_data
def load_matchups():
    matchups = pd.read_parquet('league_stats/matchups/matchups.parquet', engine='pyarrow')
    matchups['starters'] = matchups['starters'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    matchups['players'] = matchups['players'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    matchups['bench'] = matchups.apply(lambda row: [p for p in row['players'] if p not in row['starters']], axis=1)
    matchups[['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'TE', 'FL', 'K', 'DEF']] = pd.DataFrame(matchups['starters'].to_list(), index=matchups.index)
    return matchups

@st.cache_data
def load_rosters():
    rosters = pd.read_parquet('league_stats/rosters/rosters.parquet', engine='pyarrow')
    settings = rosters['settings'].apply(pd.Series)
    rosters = rosters.drop(columns=['settings']).join(settings)
    rosters['fpts'] = round(rosters['fpts'] + rosters['fpts_decimal'] / 100,2)
    rosters['fpts_against'] = round(rosters['fpts_against'] + rosters['fpts_against_decimal'] / 100,2)
    rosters['ppts'] = round(rosters['ppts'] + rosters['ppts_decimal'] / 100,2)
    rosters = rosters.drop(columns=['fpts_decimal', 'fpts_against_decimal', 'ppts_decimal', 'starters'])
    return rosters

@st.cache_data
def load_users():
    users = pd.read_parquet('league_stats/users.parquet', engine='pyarrow')
    return users

@st.cache_data
def load_players():
    players = pd.read_json('sleeper_stats/players/players.json')
    players = players.T.reset_index(drop=True)
    players["full_name"] = players["full_name"].fillna(players["last_name"])
    player_dict = players.set_index("player_id")["full_name"].to_dict()
    return players, player_dict

@st.cache_data
def get_matchup_results(matchdf, userdf):
    matchups = matchdf.groupby(["league_id", "week", "matchup_id"]).apply(
        lambda x: pd.Series({
            "winner_roster_id": x.loc[x["points"].idxmax(), "roster_id"],
            "winner_points": x["points"].max(),
            "loser_roster_id": x.loc[x["points"].idxmin(), "roster_id"],
            "loser_points": x["points"].min()
        })
    ).reset_index()

    # Merge für Gewinner-Namen
    matchups = matchups.merge(userdf, left_on=["league_id", "winner_roster_id"], right_on=["league_id", "roster_id"], how="left")
    matchups = matchups.rename(columns={"display_name": "winner_name"}).drop(columns=["roster_id", 'league_name', 'user_id', 'draft_pos'])

    # Merge für Verlierer-Namen
    matchups = matchups.merge(userdf, left_on=["league_id", "loser_roster_id"], right_on=["league_id", "roster_id"], how="left")
    matchups = matchups.rename(columns={"display_name": "loser_name"}).drop(columns=["roster_id", 'user_id', 'draft_pos'])
    return matchups

users_df = load_users()
matchups_df = load_matchups()
matchups_df = matchups_df.merge(users_df[['league_id', 'roster_id', 'display_name', 'league_name']], on=['league_id', 'roster_id'], how='left')
rosters_df = load_rosters()

players_df, players_dict = load_players()
matches_df = get_matchup_results(matchdf=matchups_df, userdf=users_df)

for pos in ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'TE', 'FL', 'K']:
    matchups_df[pos] = matchups_df[pos].map(players_dict)

rosters_df = rosters_df.merge(users_df[['display_name', 'league_name', 'league_id', 'roster_id']], on=['league_id', 'roster_id'], how='left')

# --- Startseite ---
with tab1:
    st.title("Stoned Lack Redraft 2024 -- Wochenauswertung :football:")
    st.subheader("Wöchentlicher Überblick über die SLR 2024. 35 Ligen, 420 Manager, eine App.")
    st.write("Ankündigungen, Infos, Tipps auf dem Stoned Lack [Discord-Server](https://discord.gg/V9pt9MZ6Ch).")
    st.image("Pictures/SL_logo.png", width=150)

with tab2:
    st.title('Matchup-Übersicht')
    st.write('Übersicht über alle Matchups. Filter nach Woche, Liga oder bestimmten Manager (zeigt alle gewonnenen und verlorernen Spiele).')
    matches_show = matches_df[['league_name', 'week', 'winner_name', 'winner_points', 'loser_name', 'loser_points']]
    matches_show = matches_show.rename(columns={
        'league_name' : 'Liga',
        'week' : 'Woche',
        'winner_name' : 'Gewinner',
        'winner_points' : 'Pkt. Gewinner',
        'loser_name' : 'Verlierer',
        'loser_points' : 'Pkt. Verlierer'        
    })
    matches_show['Pkt. Summe'] = matches_show['Pkt. Gewinner'] + matches_show['Pkt. Verlierer']
    matches_show['Pkt. Diff'] = matches_show['Pkt. Gewinner'] - matches_show['Pkt. Verlierer']
    # Filter-Auswahl direkt über der Tabelle
    col1, col2 = st.columns(2)

    with col1:
        filter_type = st.selectbox('Filter:', ['Alle', 'Woche', 'Liga', 'Manager'], key="filter_type")

    with col2:
        if filter_type != "Alle":
            filter_options = {
                "Woche": sorted(matches_show['Woche'].unique()),
                "Liga": sorted(matches_show['Liga'].unique()),
                "Manager": sorted(set(matches_show['Gewinner']).union(set(matches_show['Verlierer'])))
            }
            filter_value = st.selectbox(f"{filter_type} auswählen", filter_options[filter_type], key="filter_value")
        else:
            filter_value = None

    # Filter anwenden
    if filter_type == "Woche":
        matches_show = matches_show[matches_show['Woche'] == filter_value]
    elif filter_type == "Liga":
        matches_show = matches_show[matches_show['Liga'] == filter_value]
    elif filter_type == "Manager":
        matches_show = matches_show[(matches_show['Gewinner'] == filter_value) | (matches_show['Verlierer'] == filter_value)]

    # Gefilterte Tabelle anzeigen
    st.dataframe(matches_show, hide_index=True)

# --- Wochenkategorien ---
with tab3:
    st.title("Wochenkategorien")
    if not matches_df.empty:
        matches_df['pts_total'] = round(matches_df['winner_points'] + matches_df['loser_points'],2)
        matches_df['pts_diff'] = round(matches_df['winner_points'] - matches_df['loser_points'],2)
        select_week = st.selectbox("Woche auswählen", sorted(matches_df['week'].unique()), index=0)
        week_df = matches_df[matches_df['week'] == select_week]
        week_df = week_df[['league_name', 'winner_name', 'winner_points', 'loser_name', 'loser_points', 'pts_total', 'pts_diff']]
        week_df = week_df.rename(columns={
            'league_name':'Liga',
            'winner_name':'Gewinner',
            'winner_points':'Gewinner Pkt.',
            'loser_name':'Verlierer',
            'loser_points':'Verlierer Pkt.',
            'pts_total':'Matchup Pkt.',
            'pts_diff':'Pkt. Diff.'
        })

        # Shootout der Woche
        st.subheader('🔥 Shootout der Woche')
        # shootout_df = week_df.groupby(['league_id', 'matchup_id'])['points'].sum().reset_index()
        st.dataframe(week_df.sort_values(by='Matchup Pkt.', ascending=False).head(1).style.set_properties(subset=['Matchup Pkt.'], **{'background-color': 'gray'}), hide_index=True)
        
        # Klatsche der Woche
        st.subheader('💀 Klatsche der Woche')
        # klatsche_df = week_df.groupby(['league_id', 'matchup_id'])['points'].agg(lambda x: x.max() - x.min()).reset_index()
        st.dataframe(week_df.sort_values(by='Pkt. Diff.', ascending=False).head(1).style.set_properties(subset=['Pkt. Diff.'], **{'background-color': 'gray'}), hide_index=True)
        
        # Nailbiter der Woche
        st.subheader('😱 Nailbiter der Woche')
        st.dataframe(week_df.sort_values(by='Pkt. Diff.', ascending=True).head(1).style.set_properties(subset=['Pkt. Diff.'], **{'background-color': 'gray'}), hide_index=True)
        
        # Top 5 Roster
        st.subheader('🏆 Top 5 Roster')
        top_roster_df = matchups_df[matchups_df['week']==select_week]
        # top_roster_df = top_roster_df.merge(users_df[['league_id', 'roster_id', 'display_name', 'league_name']], on=['league_id', 'roster_id'], how='left')
        top_roster_df = top_roster_df[['display_name', 'points', 'league_name', 'QB', 'RB1','RB2','WR1', 'WR2', 'TE', 'FL', 'K', 'DEF']].sort_values(by='points', ascending=False).head(5)
        top_roster_df = top_roster_df.rename(columns={
            'display_name':'Manager', 'points':'Punkte', 'league_name':'Liga'
        })
        st.dataframe(top_roster_df.style.set_properties(subset=['Punkte'], **{'background-color': 'gray'}), hide_index=True)
    else:
        st.warning("Keine Daten für die ausgewählte Woche verfügbar.")

with tab4:
    st.title("Wöchentliche Statistiken")
    weeklystats_show = rosters_df[['league_name', 'display_name', 'week', 'wins','losses', 'ties', 'fpts', 'fpts_against', 'ppts']]
    weeklystats_show['St/Sit-Acc. [%]'] = round(weeklystats_show['fpts'] / weeklystats_show['ppts'] * 100,2)
    weekly_league = st.selectbox('Wähle Liga:', weeklystats_show['league_name'].unique())
    weekly_week = st.selectbox('Wähle Woche:', weeklystats_show['week'].unique())
    weeklystats_show = weeklystats_show.rename(columns={
        'league_name':'Liga',
        'display_name':'Manager',
        'week':'Woche',
        'wins':'W',
        'losses':'L',
        'ties':'T',
        'fpts':'FPTS for',
        'fpts_against':'FPTS against',
        'ppts':'Max PF'
    })
    if weekly_week != None and weekly_league != None:
        filtered_weekly = weeklystats_show[(weeklystats_show['Woche']==weekly_week) & (weeklystats_show['Liga']==weekly_league)]
    else:
        filtered_weekly = weeklystats_show
    filtered_weekly = filtered_weekly.sort_values(by=['W', 'FPTS for'], ascending=False).reset_index(drop=True)
    st.dataframe(filtered_weekly, hide_index=True)

    def get_team_info(lid, rid, rnum, matchups):
        week = 14 + rnum
        match = matchups[
            (matchups["league_id"] == lid) &
            (matchups["roster_id"] == rid) &
            (matchups["week"] == week)
        ]
        
        if not match.empty:
            return match.iloc[0]["display_name"], match.iloc[0]["points"]
        return "Unknown", 0  # Falls keine Daten gefunden werden

    def build_bracket_graph(data, league_id, matchups_df):
        dot = graphviz.Digraph(format='png')
        dot.attr(rankdir='LR', nodesep='0.9', ranksep='1.2')  # Erhöht Abstände zwischen Nodes

        for match in data:
            match_id = match["m"]
            round_num = match["r"]
            place = match.get("p")

            team1_id = match["t1"]
            team2_id = match["t2"]

            team1_name, team1_points = get_team_info(league_id, team1_id, round_num, matchups_df)
            team2_name, team2_points = get_team_info(league_id, team2_id, round_num, matchups_df)

            # HTML-Label mit fettem Teamnamen und normalem Punktestand
            label = f"""<<B>Week {14+round_num}</B><BR/><BR/><B>{team1_name}</B> ({team1_points})<BR/><B>{team2_name}</B> ({team2_points})>"""

            if place is not None:
                label = f"""<<B>Week {14+round_num} (Spiel um Platz {place})</B><BR/><BR/><B>{team1_name}</B> ({team1_points})<BR/><B>{team2_name}</B> ({team2_points})>"""

            # Füge Knoten mit Stil hinzu
            dot.node(f"M{match_id}", label=label, shape="box", style="filled", fillcolor="#f8f9fa", fontsize="12")

            # Verbindungslinien für vorherige Matches
            if "t1_from" in match:
                prev_match = match["t1_from"]
                if "w" in prev_match:
                    dot.edge(f"M{prev_match['w']}", f"M{match_id}", color="black", penwidth="2")
                elif "l" in prev_match:
                    dot.edge(f"M{prev_match['l']}", f"M{match_id}", style="dashed", color="gray")

            if "t2_from" in match:
                prev_match = match["t2_from"]
                if "w" in prev_match:
                    dot.edge(f"M{prev_match['w']}", f"M{match_id}", color="black", penwidth="2")
                elif "l" in prev_match:
                    dot.edge(f"M{prev_match['l']}", f"M{match_id}", style="dashed", color="gray")

        return dot

    # Bestimme die league_id anhand der ausgewählten Liga
    league_ids = rosters_df.loc[rosters_df['league_name'] == weekly_league, 'league_id'].unique()
    if len(league_ids) > 0:
        league_id = league_ids[0]
    else:
        st.error("Keine gültige Liga-ID gefunden.")
        st.stop()

    # API-Aufruf zur Abfrage des Playoff-Brackets
    winner_url = f"https://api.sleeper.app/v1/league/{league_id}/winners_bracket"
    loser_url = f"https://api.sleeper.app/v1/league/{league_id}/losers_bracket"
    winner_response = requests.get(winner_url)
    loser_respone = requests.get(loser_url)

    if winner_response.status_code == 200:
        winner_bracket_data = winner_response.json()
    else:
        st.error(f"Fehler beim Abrufen der Playoff-Daten: {winner_response.status_code}")
        st.stop() 
    if loser_respone.status_code == 200:
        loser_bracket_data = loser_respone.json()
    else:
        st.error(f"Fehler beim Abrufen der Playoff-Daten: {loser_respone.status_code}")
        st.stop() 
    winner_graph = build_bracket_graph(winner_bracket_data, league_id, matchups_df)
    loser_graph = build_bracket_graph(loser_bracket_data, league_id, matchups_df)
    winner_graph.graph_attr.update({'rankdir': 'LR'})
    loser_graph.graph_attr.update({'rankdir': 'LR'})
    st.title("Playoff Picture")
    st.graphviz_chart(winner_graph)
    st.title("Toilet Bowl")
    st.graphviz_chart(loser_graph)

# --- User ---
with tab5:
    st.title('SLR Manager')

    # st.selectbox()
    user_show = users_df[['league_name', 'display_name', 'roster_id', 'draft_pos', 'league_id']]
    user_show['URL'] = user_show.apply(lambda x: f'<a href="https://sleeper.com/roster/{x["league_id"]}/{x["roster_id"]}" target="_blank">Roster Link</a>', axis=1)
    user_show = user_show.rename(columns={
        'league_name': 'Liga',
        'display_name': 'Manager',
        'roster_id': 'Roster-ID',
        'draft_pos': 'Draftposition'
    })
    selected_leagues = st.multiselect("Ligen auswählen:", user_show['Liga'].unique(), default=[])

    # Falls keine Liga ausgewählt ist, zeige den gesamten DataFrame
    filtered_df = user_show if not selected_leagues else user_show[user_show['Liga'].isin(selected_leagues)]
    filtered_df = filtered_df.drop(columns=['league_id'])

    # Dataframe anzeigen
    # st.dataframe(filtered_df, hide_index=True)

    st.markdown(filtered_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# --- NFL Player ---
with tab6:
    st.write('Hier gibt es noch nichts zu sehen. Stay tuned!')
    # st.title("Wöchentliche Matchups")

    # # matches = matchups_df.groupby(['league_id', 'week', 'matchup_id'])
    
    # # Unnötige Spalten entfernen und Spaltennamen umbenennen
    # matchups_show = matchups_df[~matchups_df['matchup_id'].isin([0, None])]
    # matchups_show = matchups_show.drop(columns=['custom_points', 'players_points'])
    # matchups_show = matchups_show.rename(columns={
    #     'points': 'Punkte',
    #     'roster_id': 'Roster-ID',
    #     'matchup_id': 'Matchup-ID',
    #     'starters': 'Starter',
    #     'starters_points': 'Starter Punkte',
    #     'week': 'Woche',
    #     'league_id': 'League-ID'
    # })

    # # # Barplot für min, max und durchschnittliche Punkte pro Woche
    # # st.subheader("📊 Punkteverteilung pro Woche")
    # # stats_df = matchups_df[~matchups_df['matchup_id'].isin([0, None])].groupby("week")["points"].agg(["min", "mean", "max"]).reset_index()
    
    # # fig, ax = plt.subplots(figsize=(10, 3))
    # # sns.barplot(data=stats_df.melt(id_vars="week", var_name="Stat", value_name="Wert"), x="week", y="Wert", hue="Stat", ax=ax)
    # # # ax.set_title("Minimal, Maximal und Durchschnittlich erzielte Punkte pro Woche")
    # # ax.set_xlabel("Woche")
    # # ax.set_ylabel("Punkte")
    # # st.pyplot(fig)

    # # Annahme: matchups_show ist bereits definiert
    # columns = ['League-ID', 'Woche']

    # selected_column1 = st.selectbox("Filtern nach...", columns)
    # if selected_column1:
    #     unique_values1 = matchups_show[selected_column1].dropna().unique()
    #     selected_value1 = st.selectbox("Wert festlegen...", unique_values1)

    # min_points, max_points = st.select_slider("Punkte eingrenzen",
    #                                           options=list(range(0,225,5)),value=(0,220))

    # filtered_df = matchups_show[(matchups_show[selected_column1] == selected_value1)]
    # filtered_df = filtered_df[(filtered_df['Punkte']>=min_points) & (filtered_df['Punkte']<=max_points)]

    # st.dataframe(filtered_df, hide_index=True)

with tab7:
    st.title("Die Stoned Lack Redraft Ligen 2024")
    st.header("Settings")
    st.subheader("Roster uns sonstige Einstellungen")
    st.write("Die SLR Ligen werden mit 12 Managern gespielt. Jedes Team besteht aus 15 Spielern. Das Starting Lineup besteht aus")
    st.write("1 QB, 2 RB, 2 WR, 1 TE, 1 Flex, 1 K, 1 DST.")
    st.write("Jeder Manager erhält zu Beginn der Saison 100 $ FAAB (Waiver Budget).")
    st.subheader("Scoring")
    st.write("Das Scoring entspricht dem PPR-Scoring (1 Punkt je Reception) mit den üblichen Einstellungen. Die gesamten Scoring-Settings können nachfolgender Tabelle entnommen werden")