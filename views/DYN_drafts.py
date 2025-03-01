import streamlit as st
from Start import display_drafts

# st.write('''
#     # Dynasty Drafts''')

dyn_leagues = st.session_state["dynleagues"]
display_drafts(dyn_leagues)