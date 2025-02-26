import streamlit as st
from tools.methods import load_matchups, load_players, load_rosters, load_scoring_settings, load_users, get_matchup_results

st.title("Wochenkategorien")

matches_df = st.session_state["matchesdf"]
matchups_df = st.session_state["matchupsdf"]

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