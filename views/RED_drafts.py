import streamlit as st
from sleeper_wrapper import League, User, Drafts

st.write('''
    # Redraft Drafts''')

red_leagues = st.session_state["redleagues"]

for league_id in red_leagues:
    league = League(league_id)
    league_data = league.get_league()
    st.write(f"#### {league_data['name']}")
    
    roster_data = league.get_rosters()
    draft_id = league_data["draft_id"]
    draft = Drafts(draft_id)
    draft_data = draft.get_specific_draft()
    draft_order = draft.get_specific_draft()["draft_order"]
    picks = draft.get_all_picks()
    latest_pick = picks[-1]["metadata"]
    if latest_pick:
        pick_data = [latest_pick['first_name'], latest_pick['last_name'], latest_pick['position'], latest_pick['team']]
    col1,col2 = st.columns([1,4], vertical_alignment="center")
    with col1:
        st.write("Draftstatus")
    with col2:
        if draft_data['status'] == "complete":
            draft_status = st.success("Complete")
        elif draft_data['status'] == "pre_draft":
            draft_status = st.error("Predraft")
        else:
            draft_status = st.warning(body=str(draft_data['status']), icon=None)
    col3, col4 = st.columns([1,4])
    with col3:
        st.write("Draft-URL")
    with col4:
        st.write(f"https://sleeper.com/draft/nfl/{draft_id}")
    col5, col6 = st.columns([1,4])
    with col5:
        st.write("Latest Pick")
    with col6:
        st.write(f"{pick_data[0]} {pick_data[1]} ({pick_data[2]}), {pick_data[3]} ")