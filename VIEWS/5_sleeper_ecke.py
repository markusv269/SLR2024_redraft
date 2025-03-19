import streamlit as st

with st.expander("Sleeper Trending Players"):
    # Setze den Titel der App
    col1, col2 = st.columns(2)
    with col1:
        hours = st.slider("Zeitraum angeben (h)", min_value=6, step=6, max_value=7*24)
    with col2:
        player = st.slider("Anzahl der angezeigten Spieler", min_value=5, max_value=25)

    # Einbetten des Sleeper-Widgets mit einem IFrame
    sleeper_url = "https://sleeper.app/embed/players/nfl/trending/{}?lookback_hours={}&limit={}"
    add_url = sleeper_url.format("add", hours, player)
    drop_url = sleeper_url.format("drop", hours, player)
    col1, col2 = st.columns(2)
    with col1:
        st.components.v1.iframe(add_url, width=300, height=20+player*50, scrolling=False)
    with col2:
        st.components.v1.iframe(drop_url, width=300, height=20+player*50, scrolling=False)

# with st.expander("NFL State"):
