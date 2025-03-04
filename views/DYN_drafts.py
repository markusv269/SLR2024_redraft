import streamlit as st
from config import DYNLEAGUES
from utils import display_drafts

st.write('''
    # Dynasty Drafts''')

display_drafts(DYNLEAGUES)