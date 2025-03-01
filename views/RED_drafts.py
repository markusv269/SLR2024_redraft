import streamlit as st
from Start import display_drafts

st.write('''
    # Redraft Drafts''')

red_leagues = st.session_state["redleagues"]
display_drafts(red_leagues)