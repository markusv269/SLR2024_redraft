import streamlit as st
from tools.methods import load_matchups, load_players, load_rosters, load_scoring_settings, load_users, get_matchup_results

import streamlit as st
from sleeper_wrapper import League, Drafts
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # Moderne Zeitzonenverwaltung

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

if "dynleagues" not in st.session_state:
    st.session_state["dynleagues"] = [
        "1075126001023164416",
        "1051603386442850304",
        "1048238093331042304",
        "1076219332172095488",
        "1053143294668029952",
        "1048631053662920704",
        "1086037365413478400",
        "1049344212866576384",
        "1048538535227244544",
        "1049045384082980864",
        "1077351625959788544",
        "1070848563929825280",
        "1048364311787290624",
        "1051213152895045632",
        "1048210596396675072",
        "1066086639572795392",
        "1065679769796173824",
        "1050484015217627136",
        "1062567367819075584",
        "1050132283480522752",
        "1073663420957835264",
        "1048511690419064832",
        "1066442549130309632",
        "1075864670105399296",
        "1090714203226267648",
        "1101960833485221888",
        "1109910619613929472",
        "1127689977992757248",
        "1129857732640841728",
        "1132013019371802624",
        "1198377313197117440",
        "1109910972271075328",# IDP only
    ]     

if "redleagues" not in st.session_state:
    st.session_state["redleagues"] = [
        '1127181027346161664', 
        '1127182827986018304', 
        '1127186511226687488', 
        '1127186794254057472', 
        '1127187487081742336', 
        '1127311654766727168', 
        '1127311983902126080', 
        '1127320431490367488', 
        '1127320700513087488', 
        '1127320941060698112', 
        '1127627836090593280', 
        '1127628155113627648', 
        '1127628421636497408', 
        '1127628613802758144', 
        '1127628823345991680', 
        '1127629014883041280', 
        '1127629219200221184', 
        '1127629396468277248', 
        '1127629571702091776', 
        '1127629772399456256', 
        '1127630307857006592', 
        '1127630509913296896', 
        '1131188813214248960', 
        '1131189247203053568', 
        '1131189607904813056', 
        '1131189850369273856', 
        '1131190226912858112', 
        '1131190465321123840', 
        '1131190678035271680', 
        '1131190923725221888', 
        '1131609815362621440',
        '1131610154457165824',
        '1131892079992414208', 
        '1132672171618217984', 
        '1134223442955550720'
    ]  

st.image("Pictures/SL_logo.png", width=150)
st.logo("Pictures/SL_logo.png")
def feedback():
    return None

def display_drafts(league_ids):
    for league_id in league_ids:
        league = League(league_id)
        league_data = league.get_league()
        roster_data = league.get_rosters()
        
        draft_id = league_data.get("draft_id")
        draft = Drafts(draft_id)
        draft_data = draft.get_specific_draft()
        draft_order = draft_data.get("draft_order", {})
        draft_time = draft_data.get("start_time", None)
        
        if draft_time:
            draft_time /= 1000  # Millisekunden in Sekunden
            draft_time_utc = datetime.fromtimestamp(draft_time, tz=timezone.utc)  # UTC-Zeit
            draft_time_mesz = draft_time_utc.astimezone(ZoneInfo("Europe/Berlin"))  # In MESZ umwandeln
            draft_time_show = draft_time_mesz.strftime("%d.%m.%Y %H:%M")
        else:
            draft_time_show = "--"

        st.write(f"#### {league_data['name']} (Draft {draft_data['season']})")

        picks = draft.get_all_picks()
        latest_pick = picks[-1] if picks else None
        
        if latest_pick:
            pick_data = [
                latest_pick["metadata"].get('first_name', 'Unknown'),
                latest_pick["metadata"].get('last_name', 'Unknown'),
                latest_pick["metadata"].get('position', 'Unknown'),
                latest_pick["metadata"].get('team', 'Unknown'),
                latest_pick["round"],
                latest_pick["draft_slot"]
            ]
        else:
            pick_data = None

        col7, col8 = st.columns([1,4])
        with col7:
            st.write("Draftstart")
        with col8:
            st.write(draft_time_show, "MESZ")

        col1, col2 = st.columns([1, 4])
        with col1:
            st.write("Draftstatus")
        with col2:
            if draft_data['status'] == "complete":
                st.success("Complete")
            elif draft_data['status'] == "pre_draft":
                st.error("Predraft")
            else:
                st.warning(str(draft_data['status']))

        col3, col4 = st.columns([1, 4])
        with col3:
            st.write("Draft-URL")
        with col4:
            st.write(f"https://sleeper.com/draft/nfl/{draft_id}")

        col5, col6 = st.columns([1, 4])
        with col5:
            st.write("Latest Pick")
        with col6:
            if pick_data:
                st.write(f"{pick_data[0]} {pick_data[1]} ({pick_data[2]}), {pick_data[3]} an {pick_data[4]}.{pick_data[5]} ")
            else:
                st.write("--")

# feedback_page = st.Page(feedback(), title="Feedback")

start_page = st.Page(
    page="views/0_start.py",
    title="Das StonedLack Universum",
    icon=":material/home:",
    default=True
    )

hot_takes = st.Page(
    page="views/1_hottakes.py",
    title="Hottake-Sammlung",
    icon=":material/whatshot:"
    )

redraft_front_page = st.Page(
    page="views/RED_info.py",
    title="Die Redraftligen",
    icon=":material/home:"
    )

redraft_weekly_page = st.Page(
    page="views/RED_Wochenstatistiken.py",
    title="Wochenstatistiken",
    icon=":material/calendar_month:"
)

redraft_weekly_cat = st.Page(
    page="views/RED_Wochenkategorien.py",
    title="Wochenkategorien",
    icon=":material/bar_chart:"
)

redraft_matchups = st.Page(
    page="views/RED_Matchups.py",
    title="Matchups",
    icon=":material/sports_football:"
)

redraft_manager = st.Page(
    title="Manager",
    page="views/RED_Manager.py",
    icon=":material/groups:"
)

redraft_draft = st.Page(
    page="views/RED_drafts.py",
    title="Drafts",
    icon=":material/target:"
)

dynasty_start = st.Page(
    page="views/DYN_info.py",
    title="Dynasty",
    icon=":material/construction:"
)

dynasty_draft = st.Page(
    page="views/DYN_drafts.py",
    title="Drafts",
    icon=":material/target:"
)

pg = st.navigation(
    {
        "Start" : [
            start_page,
            hot_takes
        ],
        "Redraft" : [
            redraft_front_page,
            redraft_weekly_page,
            redraft_weekly_cat,
            redraft_matchups,
            redraft_manager,
            redraft_draft
        ],
        "Dynasty" : [
            dynasty_start,
            dynasty_draft
        ]
    }
)

st.sidebar.write("by GoKingsGo, 2025", )

pg.run()

