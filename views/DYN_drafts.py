import streamlit as st
from config import DYNLEAGUES
from utils import display_drafts  # Falls du die Draft-Funktion ausgelagert hast

st.write('''
    # Dynasty Drafts''')

display_drafts(DYNLEAGUES)