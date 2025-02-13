import streamlit as st
from modules.matchups import get_matchups

slr_league_ids = ['1127181027346161664', 
                  '1127182827986018304', 
                  '1127186511226687488', 
                  '1127186794254057472', 
                  '1127187487081742336', 
                  '1127311654766727168', 
                  '1127311983902126080', 
                  '1127320431490367488', 
                  '1127320700513087488', 
                  '1127320941060698112', 
                  '1127627836090593280', 
                  '1127628155113627648', 
                  '1127628421636497408', 
                  '1127628613802758144', 
                  '1127628823345991680', 
                  '1127629014883041280', 
                  '1127629219200221184', 
                  '1127629396468277248', 
                  '1127629571702091776', 
                  '1127629772399456256', 
                  '1127630307857006592', 
                  '1127630509913296896', 
                  '1131188813214248960', 
                  '1131189247203053568', 
                  '1131189607904813056', 
                  '1131189850369273856', 
                  '1131190226912858112', 
                  '1131190465321123840', 
                  '1131190678035271680', 
                  '1131190923725221888', 
                  '1131609815362621440', 
                  '1131610154457165824', 
                  '1131892079992414208', 
                  '1132672171618217984', 
                  '1134223442955550720']
weeks = list(range(1,18))

st.logo("Pictures/SL_logo.png", link=None, size='large')

# st.dataframe(matchups_show, hide_index=True)
# print(max_week)

st.sidebar.title("Navigation")
menu_option = st.sidebar.selectbox("Wähle eine Seite:", ["🏠 Start", "📊 Matchups", "⚙️ Einstellungen"])

if menu_option == "🏠 Start":
    st.title("Stoned Lack Redraft 2024 -- Wochenauswertung :football:")
    st.subheader("Wöchentlicher Überblick über die SLR 2024. 35 Ligen, 420 Manager, eine App.")
    st.write("Ankündigungen, Infos, Tipps auf dem Stoned Lack [Discord-Server](https://discord.gg/V9pt9MZ6Ch).")

elif menu_option == "📊 Matchups":
    st.title("Wöchentliche Matchups")

    matchups_df = get_matchups(weeks=weeks, id_list=slr_league_ids)
    # max_week = max(matchups_df['week'].unique())
    matchups_show = matchups_df[~matchups_df['matchup_id'].isin([0, None])].drop(columns=['custom_points', 'players_points'])
    matchups_show.columns = ['Punkte', 'Roster', 'Roster-ID', 'Matchup-ID', 'Starter', 'Starter Punkte', 'Woche', 'League-ID']

    columns = matchups_show.columns.tolist()
    selected_column = st.selectbox("Filtern nach...", columns)
    unique_values = matchups_show[selected_column].unique()
    selected_value = st.selectbox("Wert festlegen...", unique_values)

    filtered_df = matchups_show[matchups_show[selected_column] == selected_value]
    st.dataframe(filtered_df,hide_index=True)

elif menu_option == "⚙️ Einstellungen":
    st.title("Einstellungen")
    st.write("Hier gibt es verschiedene Optionen.")
    st.write('Test.')