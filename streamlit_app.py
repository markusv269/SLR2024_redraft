import streamlit as st
import pandas as pd
import os
import json

st.title("Stoned Lack Redraft 2024 -- Wochenauswertung :football:")
st.subheader(
    "Wöchentlicher Überblick über die SLR 2024. 35 Ligen, 420 Manager, eine App."
)

st.write("Ankündigungen, Infos, Tipps auf dem Stoned Lack [Discord-Server](https://discord.gg/V9pt9MZ6Ch).")


st.logo("Pictures/SL_logo.png", link=None, size='large')

slr_league_ids = []
weeks = list(range(1,18))
matchups_df = pd.DataFrame()

for league_id in slr_league_ids:
    for week in weeks:
        file_path = f"matchups/{week}/{league_id}.json"
        
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                matchup_data = json.load(file)
                
                # Falls JSON-Daten eine Liste enthalten, direkt in DataFrame umwandeln
                if isinstance(matchup_data, list):
                    temp_df = pd.DataFrame(matchup_data)
                else:
                    temp_df = pd.DataFrame([matchup_data])
                
                # DataFrame mergen
                matchups_df = pd.concat([matchups_df, temp_df], ignore_index=True)

print(matchups_df.head(5))