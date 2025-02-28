import streamlit as st
from sleeper_wrapper import League, User
import pandas as pd

st.write(
    '''
    # Stoned Lack Dynastys coming! _Soon!_
    
    '''
)

dynasty_leagues = [
    "1075126001023164416",
    "1051603386442850304",
    "1048238093331042304",
    "1076219332172095488",
    "1053143294668029952",
    "1048631053662920704",
    "1086037365413478400",
    "1049344212866576384",
    "1048538535227244544",
    "1049045384082980864",
    "1077351625959788544",
    "1070848563929825280",
    "1048364311787290624",
    "1051213152895045632",
    "1048210596396675072",
    "1066086639572795392",
    "1065679769796173824",
    "1050484015217627136",
    "1062567367819075584",
    "1050132283480522752",
    "1073663420957835264",
    "1048511690419064832",
    "1066442549130309632",
    "1075864670105399296",
    "1090714203226267648",
    "1101960833485221888",
    "1109910619613929472",
    "1127689977992757248",
    "1129857732640841728",
    "1132013019371802624",
    "1198377313197117440",
    "1109910972271075328",# IDP only
]

league_overview = {}

for league_id in dynasty_leagues:
    user_name = ""
    league = League(league_id)
    league_data = league.get_league()
    roster_data = league.get_rosters()
    champ = league_data["metadata"].get("latest_league_winner_roster_id",None)
    if champ:
        owner_id = next((entry["owner_id"] for entry in roster_data if entry["roster_id"] == int(champ)), None)
        if owner_id:
            user = User(owner_id)
            user_name = user.get_display_name()
    if league_data['name'] not in league_overview.keys():
        league_overview[league_data['name']] = [league_data['league_id'], league_data["avatar"], league_data["season"], user_name]
    

league_df = pd.DataFrame(league_overview).T.reset_index(drop=False).rename(columns={"index":"Liga", 0:"League-ID", 1:"avatar", 2:"Saison", 3:"Amt. Champion"})
league_df["avatar_url"] = "https://sleepercdn.com/avatars/" + league_df["avatar"].astype(str)

st.write('''
    ### Die Stoned Lack Dynasty-Ligen
    ''')
st.dataframe(
    league_df[["avatar_url", "Liga", 'Amt. Champion']],
    column_config={"avatar_url": st.column_config.ImageColumn(" ")},
    hide_index=True
)



