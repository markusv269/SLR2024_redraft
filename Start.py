import streamlit as st
from tools.methods import (
    load_matchups, load_players, load_rosters, load_users, get_matchup_results
)
from config import SCORINGSETTINGS

# Session State Initialisierung
@st.cache_data
def initialize_data():
    return {
        "userdf": load_users(),
        "matchupsdf": None,
        "rostersdf": load_rosters(),
        "playersdf": None,
        "playersdict": None,
        "matchesdf": None,
        "scoring": SCORINGSETTINGS
    }

if "session_data" not in st.session_state:
    st.session_state["session_data"] = initialize_data()

# Matchups mit Nutzernamen verknüpfen
if st.session_state["session_data"]["matchupsdf"] is None:
    userdf = st.session_state["session_data"]["userdf"]
    matchupsdf = load_matchups().merge(
        userdf[['league_id', 'roster_id', 'display_name', 'league_name']],
        on=['league_id', 'roster_id'],
        how='left'
    )
    st.session_state["session_data"]["matchupsdf"] = matchupsdf

# Spieler laden
if st.session_state["session_data"]["playersdf"] is None:
    playersdf, playersdict = load_players()
    st.session_state["session_data"].update({
        "playersdf": playersdf,
        "playersdict": playersdict
    })

# Matchup-Ergebnisse berechnen
if st.session_state["session_data"]["matchesdf"] is None:
    st.session_state["session_data"]["matchesdf"] = get_matchup_results(
        matchdf=st.session_state["session_data"]["matchupsdf"],
        userdf=st.session_state["session_data"]["userdf"]
    )

# if "dynleagues" in st.session_state:
#     display_drafts(st.session_state["dynleagues"])

# if "redleagues" in st.session_state:
#     display_drafts(st.session_state["redleagues"])

# Streamlit UI
st.image("Pictures/SL_logo.png", width=150)
st.sidebar.write("by GoKingsGo, 2025")

# Navigation
pg = st.navigation(
    {
        "Start": [
            st.Page(page="views/0_start.py", title="Das StonedLack Universum", icon=":material/home:", default=True),
            st.Page(page="views/1_hottakes.py", title="Hot Takes-Sammlung", icon=":material/whatshot:"),
            st.Page(page="views/2_champofchamps.py", title="Champ of Champs", icon=":material/trophy:")
        ],
        "Redraft": [
            # st.Page(page="views/RED_slr2025.py", title="SLR2025 Anmeldung", icon=":material/login:"),
            # st.Page(page="views/RED_slr2025_status.py", title="SLR2025 Anmeldestatus", icon=":material/download_done:"),
            st.Page(page="views/RED_info.py", title="Die Redraftligen", icon=":material/home:"),
            st.Page(page="views/RED_uebersicht.py", title="Ligenübersicht", icon=":material/layers:"),
            st.Page(page="views/RED_alte_Redrafts.py", title="Send your old SLR", icon=":material/send:"),
            st.Page(page="views/RED_Wochenstatistiken.py", title="Wochenstatistiken", icon=":material/calendar_month:"),
            st.Page(page="views/RED_Wochenkategorien.py", title="Wochenkategorien", icon=":material/bar_chart:"),
            st.Page(page="views/RED_Matchups.py", title="Matchups", icon=":material/sports_football:"),
            st.Page(page="views/RED_Manager.py", title="Manager", icon=":material/groups:"),
            st.Page(page="views/RED_drafts.py", title="Drafts", icon=":material/target:")
        ],
        "Dynasty": [
            st.Page(page="views/DYN_info.py", title="Dynasty", icon=":material/construction:"),
            st.Page(page="views/DYN_drafts.py", title="Drafts", icon=":material/target:")
        ]
    }
)
pg.run()
