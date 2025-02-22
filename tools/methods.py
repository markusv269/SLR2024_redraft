import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st

# --- Daten laden mit Caching ---
@st.cache_data
def load_matchups():
    matchups = pd.read_parquet('league_stats/matchups/matchups.parquet', engine='pyarrow')
    matchups['starters'] = matchups['starters'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    matchups['players'] = matchups['players'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    matchups['bench'] = matchups.apply(lambda row: [p for p in row['players'] if p not in row['starters']], axis=1)
    matchups[['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'TE', 'FL', 'K', 'DEF']] = pd.DataFrame(matchups['starters'].to_list(), index=matchups.index)
    return matchups

@st.cache_data
def load_rosters():
    rosters = pd.read_parquet('league_stats/rosters/rosters.parquet', engine='pyarrow')
    settings = rosters['settings'].apply(pd.Series)
    rosters = rosters.drop(columns=['settings']).join(settings)
    rosters['fpts'] = round(rosters['fpts'] + rosters['fpts_decimal'] / 100,2)
    rosters['fpts_against'] = round(rosters['fpts_against'] + rosters['fpts_against_decimal'] / 100,2)
    rosters['ppts'] = round(rosters['ppts'] + rosters['ppts_decimal'] / 100,2)
    rosters = rosters.drop(columns=['fpts_decimal', 'fpts_against_decimal', 'ppts_decimal', 'starters'])
    return rosters

@st.cache_data
def load_users():
    users = pd.read_parquet('league_stats/users.parquet', engine='pyarrow')
    return users

@st.cache_data
def load_players():
    players = pd.read_json('sleeper_stats/players/players.json')
    players = players.T.reset_index(drop=True)
    players["full_name"] = players["full_name"].fillna(players["last_name"])
    player_dict = players.set_index("player_id")["full_name"].to_dict()
    return players, player_dict

@st.cache_data
def get_matchup_results(matchdf, userdf):
    matchups = matchdf.groupby(["league_id", "week", "matchup_id"]).apply(
        lambda x: pd.Series({
            "winner_roster_id": x.loc[x["points"].idxmax(), "roster_id"],
            "winner_points": x["points"].max(),
            "loser_roster_id": x.loc[x["points"].idxmin(), "roster_id"],
            "loser_points": x["points"].min()
        })
    ).reset_index()

    # Merge für Gewinner-Namen
    matchups = matchups.merge(userdf, left_on=["league_id", "winner_roster_id"], right_on=["league_id", "roster_id"], how="left")
    matchups = matchups.rename(columns={"display_name": "winner_name"}).drop(columns=["roster_id", 'league_name', 'user_id', 'draft_pos'])

    # Merge für Verlierer-Namen
    matchups = matchups.merge(userdf, left_on=["league_id", "loser_roster_id"], right_on=["league_id", "roster_id"], how="left")
    matchups = matchups.rename(columns={"display_name": "loser_name"}).drop(columns=["roster_id", 'user_id', 'draft_pos'])
    return matchups

@st.cache_data
def load_scoring_settings():
    scoring_settings = {
        "sack": 1,
        "fgm_40_49": 4,
        "pass_int": -1,
        "pts_allow_0": 10,
        "pass_2pt": 2,
        "st_td": 6,
        "rec_td": 6,
        "fgm_30_39": 3,
        "xpmiss": -1,
        "rush_td": 6,
        "rec_2pt": 2,
        "st_fum_rec": 1,
        "fgmiss": -1,
        "ff": 1,
        "rec": 1,
        "pts_allow_14_20": 1,
        "fgm_0_19": 3,
        "int": 2,
        "def_st_fum_rec": 1,
        "fum_lost": -2,
        "pts_allow_1_6": 7,
        "kr_yd": 0,
        "fgm_20_29": 3,
        "pts_allow_21_27": 0,
        "xpm": 1,
        "rush_2pt": 2,
        "fum_rec": 2,
        "def_st_td": 6,
        "fgm_50p": 5,
        "def_td": 6,
        "safe": 2,
        "pass_yd": 0.04,
        "blk_kick": 2,
        "pass_td": 4,
        "rush_yd": 0.1,
        "pr_yd": 0,
        "fum": -1,
        "pts_allow_28_34": -1,
        "pts_allow_35p": -4,
        "fum_rec_td": 6,
        "rec_yd": 0.1,
        "def_st_ff": 1,
        "pts_allow_7_13": 4,
        "st_ff": 1
    }
    return scoring_settings