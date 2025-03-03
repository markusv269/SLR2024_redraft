import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sleeper_wrapper import League, Drafts, User  # Falls du diese API nutzt

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
        draft_type = draft_data["settings"].get("player_type")
        draft_mode = draft_data["type"]

        if draft_type == 0:
            draft_typ = "Rookie + Veteran Draft"
        elif draft_type == 1:
            draft_typ = "Rookie Draft"
        elif draft_type == 2:
            draft_typ = "Veteran Draft"
        else:
            draft_typ = "Draft"

        if draft_time:
            draft_time /= 1000  # Millisekunden in Sekunden
            draft_time_utc = datetime.fromtimestamp(draft_time, tz=timezone.utc)  # UTC-Zeit
            draft_time_mesz = draft_time_utc.astimezone(ZoneInfo("Europe/Berlin"))  # In MESZ umwandeln
            draft_time_show = draft_time_mesz.strftime("%d.%m.%Y %H:%M")
        else:
            draft_time_show = "--"

        st.write(f"#### {league_data['name']}")

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
        col11, col12 = st.columns([1,4])
        with col11:
            st.write("Draftmodus")
        with col12:
            st.write(f"{draft_typ} ({draft_mode}) {draft_data['season']}")

        col7, col8 = st.columns([1,4])
        with col7:
            st.write("Draftstart")
        with col8:
            st.write(draft_time_show)

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

        with st.expander("Draftdetails anzeigen"):
            col5, col6 = st.columns([1, 4])
            with col5:
                st.write("Latest Pick")
            with col6:
                if pick_data:
                    st.write(f"{pick_data[0]} {pick_data[1]} ({pick_data[2]}), {pick_data[3]} an {pick_data[4]}.{pick_data[5]} ")
                else:
                    st.write("--")

            # Draftorder in einer Tabelle anzeigen
            if draft_order:
                draft_list = []
                for user_id, draft_pos in draft_order.items():
                    user = User(user_id)
                    user_name = user.get_display_name()
                    draft_list.append({"Draft Position": draft_pos, "Manager": user_name})
                col9, col10 = st.columns([1,4])
                with col9:
                    st.write("Draftorder")
                with col10:
                    # Sortieren nach Draft-Position
                    draft_df = pd.DataFrame(draft_list).sort_values(by="Draft Position")
                    st.table(draft_df.set_index("Draft Position"))
            else:
                st.write("No draft order available.")


