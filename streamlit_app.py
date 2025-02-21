import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st
import graphviz
import json
import requests
import os

# --- Streamlit-Setup ---
st.set_page_config(page_title="SLR 2024 Dashboard", layout="wide")
tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs(["🏠 Start", "📊 Matchups", "📅 Wochenkategorien", "📋 Statistiken", "👨‍👨‍👧‍👦 Users", "NFL Player", "SLR Ligen", "Sandbox"])

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

@st.cache_data
def load_scoring_settings():
    scoring_settings = {
        "sack": 1,
        "fgm_40_49": 4,
        "pass_int": -1,
        "pts_allow_0": 10,
        "pass_2pt": 2,
        "st_td": 6,
        "rec_td": 6,
        "fgm_30_39": 3,
        "xpmiss": -1,
        "rush_td": 6,
        "rec_2pt": 2,
        "st_fum_rec": 1,
        "fgmiss": -1,
        "ff": 1,
        "rec": 1,
        "pts_allow_14_20": 1,
        "fgm_0_19": 3,
        "int": 2,
        "def_st_fum_rec": 1,
        "fum_lost": -2,
        "pts_allow_1_6": 7,
        "kr_yd": 0,
        "fgm_20_29": 3,
        "pts_allow_21_27": 0,
        "xpm": 1,
        "rush_2pt": 2,
        "fum_rec": 2,
        "def_st_td": 6,
        "fgm_50p": 5,
        "def_td": 6,
        "safe": 2,
        "pass_yd": 0.04,
        "blk_kick": 2,
        "pass_td": 4,
        "rush_yd": 0.1,
        "pr_yd": 0,
        "fum": -1,
        "pts_allow_28_34": -1,
        "pts_allow_35p": -4,
        "fum_rec_td": 6,
        "rec_yd": 0.1,
        "def_st_ff": 1,
        "pts_allow_7_13": 4,
        "st_ff": 1
    }
    return scoring_settings

users_df = load_users()
matchups_df = load_matchups()
matchups_df = matchups_df.merge(users_df[['league_id', 'roster_id', 'display_name', 'league_name']], on=['league_id', 'roster_id'], how='left')
rosters_df = load_rosters()

players_df, players_dict = load_players()
matches_df = get_matchup_results(matchdf=matchups_df, userdf=users_df)

for pos in ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'TE', 'FL', 'K']:
    matchups_df[pos] = matchups_df[pos].map(players_dict)

rosters_df = rosters_df.merge(users_df[['display_name', 'league_name', 'league_id', 'roster_id']], on=['league_id', 'roster_id'], how='left')
scoring_settings = load_scoring_settings()
# --- Startseite ---
with tab1:
    st.title("Stoned Lack Redraft 2024 -- Wochenauswertung :football:")
    st.subheader("Wöchentlicher Überblick über die SLR 2024. 35 Ligen, 420 Manager, eine App.")
    st.write("Ankündigungen, Infos, Tipps auf dem Stoned Lack [Discord-Server](https://discord.gg/V9pt9MZ6Ch).")
    st.image("Pictures/SL_logo.png", width=150)

with tab2:
    st.title('Matchup-Übersicht')
    st.write('''Übersicht über alle Matchups. Filter nach Woche, Liga oder bestimmten Manager (zeigt alle gewonnenen und verlorernen Spiele).
             \n_Aus Performance-Gründen werden maximal 100 Matchups angezeigt._''')

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
   
   
    # Filter-UI
    ucol1, ucol2, ucol3 = st.columns([1, 1, 1.6])
    dcol1, dcol2, dcol3 = st.columns([1, 1, 1.6])

    with ucol1:
        activate_league = st.checkbox("Ligafilter aktivieren", key="cb_league")
    with ucol2:
        activate_week = st.checkbox("Wochenfilter aktivieren", key="cb_week")

    # Bedingte Filteroptionen
    with dcol1:
        select_league = st.selectbox("Wähle Liga", matches_show["Liga"].unique(), key="sel_league") if activate_league else None
    with dcol2:
        select_week = st.selectbox("Wähle Woche", sorted(matches_show["Woche"].unique()), key="sel_week") if activate_week else None
    with dcol3:
        select_manager = st.multiselect("Manager wählen", sorted(set(matches_show["Gewinner"]).union(set(matches_show["Verlierer"]))))

    # Daten filtern
    filtered_df = matches_show.copy()

    if activate_league and select_league:
        filtered_df = filtered_df[filtered_df["Liga"] == select_league]

    if activate_week and select_week:
        filtered_df = filtered_df[filtered_df["Woche"] == select_week]

    if select_manager:
        filtered_df = filtered_df[filtered_df["Gewinner"].isin(select_manager) | filtered_df["Verlierer"].isin(select_manager)]

    # Dynamische Spaltenauswahl
    column_order = [col for col in filtered_df.columns if col not in (["Liga"] if activate_league else []) + (["Woche"] if activate_week else [])]

    # Gefilterte Tabelle anzeigen
    # st.dataframe(filtered_df, column_order=column_order, hide_index=True)
    filtered_df = filtered_df.head(100)

    st.write("### Matchups")
    matchups_per_row = 4
    rows = [filtered_df.iloc[i:i+matchups_per_row] for i in range(0, len(filtered_df), matchups_per_row)]

    for row in rows:
        cols = st.columns(matchups_per_row)
        for col, (_, matchup) in zip(cols, row.iterrows()):
            with col:
                st.markdown(
                    f"""
                    <div style="border:1px solid #ddd; border-radius:10px; padding:10px; text-align:center; background-color:#f9f9f9;">
                        <div style="font-size:11px; font-weight:bold; color:#555;">{matchup['Liga']} - Woche {matchup['Woche']}</div>
                        <hr style="margin:5px 0; border-top:1px solid #ddd;">
                        <div style="font-size:16px; font-weight:bold; color:#28a745;">{matchup['Gewinner']}</div>
                        <div style="font-size:13px; color:gray;">{matchup['Pkt. Gewinner']:.2f}</div>
                        <div style="font-size:20px; font-weight:bold;">:</div>
                        <div style="font-size:13px; color:gray;">{matchup['Pkt. Verlierer']:.2f}</div>
                        <div style="font-size:16px; font-weight:bold; color:#dc3545;">{matchup['Verlierer']}</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    # st.subheader("Alle Matchups eines Managers")


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

    def calculate_fantasy_points(stats, scoring_settings):
        """Berechnet Fantasy-Punkte basierend auf stats und scoring_settings."""
        return sum(stats.get(stat, 0) * scoring_settings.get(stat, 0) for stat in scoring_settings.keys())

    def load_player_data(json_file, scoring_settings, is_projection=True):
        """Lädt relevante Spielerstatistiken aus einer JSON-Datei (Projections oder Stats)."""
        if not os.path.exists(json_file):
            # print(f"❌ Datei nicht gefunden: {json_file}")
            return {}

        with open(json_file, 'r') as f:
            data = json.load(f)

        player_data = {}

        if is_projection:
            # Projections sind Listen mit Dictionaries
            if isinstance(data, list):
                for entry in data:
                    player_id = entry.get("player_id")
                    stats = entry.get("stats", {})

                    # Nur relevante Stats extrahieren
                    filtered_stats = {stat: value for stat, value in stats.items() if stat in scoring_settings}

                    if player_id and filtered_stats:
                        player_data[player_id] = filtered_stats
            else:
                None
                # print(f"⚠ Unerwartetes JSON-Format in {json_file} für Projections")

        else:
            # Stats sind Dictionaries mit player_id als Schlüssel
            if isinstance(data, dict):
                for player_id, stats in data.items():
                    filtered_stats = {stat: value for stat, value in stats.items() if stat in scoring_settings}

                    if filtered_stats:
                        player_data[player_id] = filtered_stats
            else:
                None
                # print(f"⚠ Unerwartetes JSON-Format in {json_file} für Stats")

        # print(f"✅ Geladene Spieler aus {json_file}: {len(player_data)} Spieler")
        return player_data

    def create_combined_df(weeks, scoring_settings):
        """Erstellt ein DataFrame mit 'player_id' sowie proj und stats als Listen über alle Wochen."""
        all_data = {}

        for week in weeks:
            proj_file = f"sleeper_stats/projections/projection_{week}.json"
            stats_file = f"sleeper_stats/stats/stats_{week}.json"

            # Projections laden
            proj_stats = load_player_data(proj_file, scoring_settings, is_projection=True)
            for player_id, stats in proj_stats.items():
                if player_id not in all_data:
                    all_data[player_id] = {"proj": [], "stats": []}  # Initialisierung
                all_data[player_id]["proj"].append(calculate_fantasy_points(stats, scoring_settings))

            # Tatsächliche Stats laden
            actual_stats = load_player_data(stats_file, scoring_settings, is_projection=False)
            for player_id, stats in actual_stats.items():
                if player_id not in all_data:
                    all_data[player_id] = {"proj": [], "stats": []}  # Initialisierung
                all_data[player_id]["stats"].append(calculate_fantasy_points(stats, scoring_settings))

        # DataFrame erstellen
        df = pd.DataFrame.from_dict(all_data, orient="index").reset_index()
        df.rename(columns={"index": "player_id"}, inplace=True)

        return df

    # Beispiel: Wochen 1-5
    weeks = range(1, 19)

    df_combined = create_combined_df(weeks, scoring_settings)

    players_df = players_df.merge(df_combined, on='player_id', how='right')

    # Ausgabe in Streamlit
    players_show = players_df[['full_name', 'team', 'position', "stats", "proj"]]
    # players_show['fpts_total'] = players_show[[f"stats_{week}" for week in weeks]].sum(axis=1)
    # players_show['proj_total'] = players_show[[f"proj_{week}" for week in weeks]].sum(axis=1)

    players_show = players_show.dropna(subset=['full_name'], axis=0)

    def display_df(df):
        st.dataframe(
            df,
            column_order=[
                column
                for column in list(df.columns)
                if column in [
                    'full_name',
                    'team',
                    'position',
                    "stats",
                    "proj"
                ]
            ],
            column_config={
                "stats": st.column_config.AreaChartColumn(
                    "Stats",
                    width="medium",
                    help="Fantasy Points per Week"),
                "proj": st.column_config.AreaChartColumn(
                    "Projection",
                    width="medium",
                    help="Projected Fantasy Points per Week"),
            },
            hide_index=True,
            height=2500
        )
    display_df(players_show)

with tab7:
    st.title("Die Stoned Lack Redraft Ligen 2024")
    st.header("Settings")
    # st.subheader("Roster uns sonstige Einstellungen")
    st.write("Die SLR Ligen werden mit 12 Managern gespielt. Jedes Team besteht aus 15 Spielern. Das Starting Lineup besteht aus")
    st.write("1 QB, 2 RB, 2 WR, 1 TE, 1 Flex, 1 K, 1 DST.")
    st.write("Jeder Manager erhält zu Beginn der Saison 100 $ FAAB (Waiver Budget).")
    st.header("Scoring")
    st.write("Das Scoring entspricht dem PPR-Scoring (1 Punkt je Reception) mit den üblichen Einstellungen. Die gesamten Scoring-Settings können den nachfolgenden Tabellen entnommen werden")

    # Kategorien definieren
    categories = {
        "Passing": ["pass_yd", "pass_td", "pass_2pt", "pass_int"],
        "Rushing": ["rush_yd", "rush_td", "rush_2pt"],
        "Receiving": ["rec_yd", "rec_td", "rec_2pt", "rec"],
        "Special Teams": ["st_td", "st_fum_rec", "st_ff", "kr_yd", "pr_yd"],
        "Defense": ["sack", "int", "ff", "fum_rec", "fum_rec_td", "def_td", "safe", "blk_kick", "def_st_ff", "def_st_fum_rec", "def_st_td"],
        "Kicking": ["fgm_0_19", "fgm_20_29", "fgm_30_39", "fgm_40_49", "fgm_50p", "fgmiss", "xpm", "xpmiss"],
    }

    # Beschreibungen der Stats
    descriptions = {
        "pass_yd": "Passing Yards (pro Yard)",
        "pass_td": "Passing Touchdown",
        "pass_2pt": "2-Punkt-Conversion (Pass)",
        "pass_int": "Interception geworfen",
        "rush_yd": "Rushing Yards (pro Yard)",
        "rush_td": "Rushing Touchdown",
        "rush_2pt": "2-Punkt-Conversion (Rush)",
        "rec_yd": "Receiving Yards (pro Yard)",
        "rec_td": "Receiving Touchdown",
        "rec_2pt": "2-Punkt-Conversion (Receiving)",
        "rec": "Reception (gefangener Pass)",
        "st_td": "Special Teams Touchdown",
        "st_fum_rec": "Special Teams Fumble Recovery",
        "st_ff": "Special Teams Forced Fumble",
        "sack": "Quarterback Sack",
        "int": "Interception gefangen",
        "ff": "Forced Fumble",
        "fum_rec": "Fumble Recovery",
        "fum_rec_td": "Fumble Recovery Touchdown",
        "def_td": "Defensive Touchdown",
        "safe": "Safety",
        "blk_kick": "Blocked Kick",
        "def_st_ff": "Defense/Special Teams Forced Fumble",
        "def_st_fum_rec": "Defense/Special Teams Fumble Recovery",
        "def_st_td": "Defense/Special Teams Touchdown",
        "fgm_0_19": "Field Goal (0-19 Yards) verwandelt",
        "fgm_20_29": "Field Goal (20-29 Yards) verwandelt",
        "fgm_30_39": "Field Goal (30-39 Yards) verwandelt",
        "fgm_40_49": "Field Goal (40-49 Yards) verwandelt",
        "fgm_50p": "Field Goal (50+ Yards) verwandelt",
        "fgmiss": "Field Goal verschossen",
        "xpm": "Extra Punkt verwandelt",
        "xpmiss": "Extra Punkt verschossen",
        "pts_allow_0": "Gegnerische Punkte: 0",
        "pts_allow_1_6": "Gegnerische Punkte: 1-6",
        "pts_allow_7_13": "Gegnerische Punkte: 7-13",
        "pts_allow_14_20": "Gegnerische Punkte: 14-20",
        "pts_allow_21_27": "Gegnerische Punkte: 21-27",
        "pts_allow_28_34": "Gegnerische Punkte: 28-34",
        "pts_allow_35p": "Gegnerische Punkte: 35+",
    }

    # Daten für die Tabelle sammeln
    for category, keys in categories.items():
        data = []
        for key in keys:
            if key in scoring_settings:
                data.append({
                    # "Kategorie": category,
                    "Sleeper-Stat": key,
                    "Beschreibung": descriptions.get(key, "Keine Beschreibung verfügbar"),
                    "Punkte": scoring_settings[key]
                })
    
        if data:
            df = pd.DataFrame(data)
            st.subheader(category)
            st.dataframe(df.set_index("Sleeper-Stat"), hide_index=True)


# with tab8:
#     def column_manager(df1,df2):
#         left_widget, right_widget, _ = st.columns([1,1,1.5])
#         selected_ticker = left_widget.selectbox(
#             "Filter:",
#             list(df1.keys()),
#         )
#         selected_period = right_widget.selectbox(
#             "Period",
#             ("Week", "League", "Manager"),
#             2,
#         )
#         st.header(selected_ticker)
#         st.header(selected_period)
    
#     column_manager(players_df, matches_df)
#     # st.json(scoring_settings)