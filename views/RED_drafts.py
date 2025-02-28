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
    draft_order = draft_data.get("draft_order", {})
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

    col1, col2 = st.columns([1, 4], vertical_alignment="center")
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