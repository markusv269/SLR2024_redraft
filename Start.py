import streamlit as st
from tools.methods import load_matchups, load_players, load_rosters, load_scoring_settings, load_users, get_matchup_results

# st.set_page_config(page_title="Start", page_icon="🍎")
st.title("Stoned Lack Redraft 2024 -- Wochenauswertung :football:")
st.subheader("Wöchentlicher Überblick über die SLR 2024. 35 Ligen, 420 Manager, eine App.")
st.write("Ankündigungen, Infos, Tipps auf dem Stoned Lack [Discord-Server](https://discord.gg/V9pt9MZ6Ch).")
st.image("Pictures/SL_logo.png", width=150)


if "userdf" not in st.session_state:
    st.session_state['userdf'] = load_users()
if "matchupsdf" not in st.session_state:
    matchupsdf = load_matchups().merge(st.session_state["userdf"][['league_id', 'roster_id', 'display_name', 'league_name']], on=['league_id', 'roster_id'], how='left')
    st.session_state["matchupsdf"] = matchupsdf
if "rostersdf" not in st.session_state:
    st.session_state["rostersdf"] = load_rosters()
if "playersdf" and "playersdict" not in st.session_state:
    st.session_state["playersdf"], st.session_state["playersdict"] = load_players()
if "matchesdf" not in st.session_state:
    st.session_state["matchesdf"] = get_matchup_results(
        matchdf=st.session_state["matchupsdf"],
        userdf=st.session_state["userdf"]
        )
if "scoring" not in st.session_state:
    st.session_state["scoring"] = load_scoring_settings()