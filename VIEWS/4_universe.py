import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import requests
from config import DYNLEAGUES, REDLEAGUES

# Vorgegebene Ligen
LEAGUE_IDS = DYNLEAGUES + REDLEAGUES
st.title("Das StonedLack Universum")
st.write("_Das Laden des Ligen-Netzwerkes dauert ein wenig!_")

# Beispielhafte Liste von League IDs
league_ids = LEAGUE_IDS

# Funktion zum Abrufen des Namens der Liga für eine gegebene League ID
def get_league_data(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        league_data = response.json()
        return league_data
    else:
        st.error(f"Fehler beim Abrufen des Namens der Liga {league_id}")
        return 'Unbekannte Liga'

# Funktion zum Abrufen der Benutzerdaten für eine gegebene League ID
def get_users_from_league(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}/users"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Gibt eine Liste der Benutzer zurück
    else:
        st.error(f"Fehler beim Abrufen der Daten für League {league_id}")
        return []

# Erstelle Knoten und Kanten basierend auf den Daten
def prepare_data(selected_leagues=None, search_query=None):
    nodes = []
    edges = []
    for league_id in league_ids:
        if selected_leagues and league_id not in selected_leagues:
            continue  # Nur ausgewählte Ligen berücksichtigen

        league_name = get_league_data(league_id).get('name', 'Unbekannte Liga')  # Rückgabe des Namens oder 'Unbekannte Liga', wenn Name nicht vorhanden  # Liga-Name abrufen
        draft_id = get_league_data(league_id).get('draft_id', 'keine')
        users = get_users_from_league(league_id)
        
        # Füge einen Knoten für jede Liga hinzu, mit dem Namen der Liga
        nodes.append({"data": {"id": f"league_{league_id}", "label": "LEAGUE", "name": league_name, "Draft-ID":draft_id}})
        
        for user in users:
            if search_query and search_query.lower() not in user['display_name'].lower():
                continue  # Wenn nach einem Benutzer gesucht wird, nur Benutzer anzeigen, die dem Suchbegriff entsprechen
            user_id = user['user_id']
            display_name = user['display_name']
            
            # Füge einen Knoten für jeden Benutzer hinzu
            nodes.append({"data": {"id": f"user_{user_id}", "label": "USER", "name": display_name}})
            
            # Füge eine Kante von der Liga zum Benutzer hinzu
            edges.append({"data": {"id": f"edge_{league_id}_{user_id}", "label": "PARTICIPATES", "source": f"league_{league_id}", "target": f"user_{user_id}"}})

    return {"nodes": nodes, "edges": edges}

# UI für die Auswahl der Ligen mit den Liganamen
league_names = [get_league_data(league_id).get('name', 'Unbekannte Liga') for league_id in league_ids]
st.markdown("### Wähle eine oder mehrere Ligen aus:")
selected_league_names = st.multiselect(
    "Ligen auswählen",
    options=league_names,
    # default=league_names  # Standardmäßig alle Ligen ausgewählt
)

# Umwandlung der ausgewählten Liganamen in die zugehörigen League IDs
selected_leagues_ids = [league_ids[league_names.index(name)] for name in selected_league_names]

# UI für die Benutzersuche
search_query = st.text_input("Benutzer suchen (Teil des Namens)")

# Bereite die Daten basierend auf den Benutzerangaben vor
elements = prepare_data(selected_leagues_ids, search_query)

# Style node & edge groups
node_styles = [
    NodeStyle("LEAGUE", "#FF7F3E", "name", "league"),
    NodeStyle("USER", "#2A629A", "name", "user"),
]

edge_styles = [
    EdgeStyle("PARTICIPATES", directed=False),
]

# Render the component
st_link_analysis(elements, "cose", node_styles, edge_styles)