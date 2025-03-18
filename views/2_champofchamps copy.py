import streamlit as st
import pandas as pd
import json
from views.CoC.config import COC, scoring_settings, wc_round_player, div_round_player, conf_round_player, super_bowl_player, conf_round_groups

WC_tips = pd.DataFrame.from_dict(COC["WC"], orient="index")
WC_player = pd.DataFrame.from_dict(wc_round_player, orient="index")#.reset_index(drop=False)

# JSON-Datei laden
with open("views/CoC/wc.json", encoding="utf-8") as f:
    WC_stats = json.load(f)

# Sicherstellen, dass WC_stats ein DataFrame ist
WC_stats = pd.DataFrame(WC_stats)
WC_stats = WC_stats[WC_stats["player_id"].isin(WC_player["player_id"].unique())]

# DataFrames in Streamlit anzeigen
st.dataframe(WC_tips)
st.dataframe(WC_player)
st.write(WC_stats)