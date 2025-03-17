import streamlit as st
import pandas as pd
import json
from views.CoC.config import COC, scoring_settings, wc_round_player, div_round_player, conf_round_player, super_bowl_player, conf_round_groups

WC_tips = pd.DataFrame.from_dict(COC["WC"],orient="index")
WC_player = pd.DataFrame.from_dict(wc_round_player, orient="index")
# WC_tips = WC_tips.merge(WC_player, on)
st.dataframe(WC_tips)
st.dataframe(WC_player)