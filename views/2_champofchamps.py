import streamlit as st
import pandas as pd
import json
from views.CoC.config import COC, scoring_settings, wc_round_player, div_round_player, conf_round_player, super_bowl_challenge

# Benutzerdefinierte Sortierreihenfolge für Positionen
position_order = ["QB", "RB", "WR", "TE"]

# Funktion zum Hinzufügen des Preises aus den jeweiligen Runden
def add_price(player_id, round_player_data):
    # Iterate over the dictionary items: (player_name, player_info)
    for player_name, player_info in round_player_data.items():
        if player_info['player_id'] == player_id:
            return player_info['price']
    return 0  # Default value if the player isn't found

# Sortiere den DataFrame nach Position und Preis (absteigend)
def ind_calculate_fantasy_points_and_sort(json_file, round_player_data, scoring_settings):
    with open(json_file, encoding="utf-8") as f:
        stats_data = json.load(f)

    valid_player_ids = {data["player_id"] for data in round_player_data.values()}
    data = []

    # Spieler filtern und ihre Stats extrahieren
    for player in stats_data:
        if player["player_id"] in valid_player_ids:
            player_name = player['player'].get("first_name", "") + " " + player['player'].get("last_name", "")
            player_data = {
                "player_id": player["player_id"],
                "Spieler": player_name,  # Spielernamen hinzufügens
                "Position": player["player"]["position"],
                "Gruppe": player["team"],
                "FFP": 0
            }

            # Preis aus der Runde hinzufügen
            player_data["Preis"] = add_price(player["player_id"], round_player_data)

            # Fantasy-Punkte berechnen
            fantasy_points = 0
            for key, multiplier in scoring_settings.items():
                stat_value = player.get("stats", {}).get(key, 0)  # Falls Wert fehlt, setze 0
                player_data[key] = stat_value
                fantasy_points += stat_value * multiplier  # Punkte berechnen

            # Finalen Punktestand speichern
            player_data["FFP"] = round(fantasy_points, 2)  # Runden für bessere Lesbarkeit

            data.append(player_data)

    # DataFrame erstellen
    df = pd.DataFrame(data)

    # Position sortieren mit benutzerdefinierter Reihenfolge und Preis absteigend
    df["Position"] = pd.Categorical(df["Position"], categories=position_order, ordered=True)
    df = df.sort_values(by=["Position", "Preis"], ascending=[True, False])
    df = df[['player_id', "Spieler", "Position", "Gruppe", "FFP", "Preis"]].set_index("player_id")

    return df

# Streamlit-Setup
st.write("# Champ of Champs 2024")
st.write('''Das Champ of Champs-Spiel ist der Abschluss der StonedLack-Saison und kührt den Sieger aller Sieger aus den StonedLack-Ligen.
         Zugelassen waren dieses Jahr alle Champions aus den aktuellen Redraftligen (Saison 2024) sowie alle Dynasty-Champs der StonedLack Dynastys.

Die ersten drei Runden (Wild Card Weekend, Divisional Round und Conference Finals) bestanden aus dem $9-Game. Ziel ist, ein Team aus QB, RB, WR und TE zusammen zu stellen. Das Budget darf 9 Dollar nicht überschreiten. Die Werte der Spieler sind den Grafiken zu entnehmen. Als Besonderheit wurden bei den Conference Finals für die RB- und WR-Position jeweils Spielerpaare aus den Teams gewertet.

Im Superbowl wurden drei Spieler frei ihrer Position gewählt. Jeder Spieler hat einen Multiplikator, mit dem seine Fantasy-Punkte multipliziert werden.

In jeder Runde galt es, möglichst viele Punkte zu erreichen. Gesamtsieger ist der oder diejenige mit den meisten Punkten nach dem Superbowl.

Stonis Auswertung findet ihr im Discord im entsprechenden Kanal!
## Das Scoring''')
st.table(scoring_settings)



# Wild Card Weekend
st.write("## Wild Card Weekend")
st.write("### Tippbild")
st.image("Pictures/WC.jfif", width=500)
wc_df = ind_calculate_fantasy_points_and_sort("views/CoC/wc.json", wc_round_player, scoring_settings)
st.write("### Fantasyergebnisse")
st.dataframe(wc_df, hide_index=True)

# Divisional Round
st.write("## Divisional Round")
st.write("### Tippbild")
st.image("Pictures/DR.png", width=500)
dr_df = ind_calculate_fantasy_points_and_sort("views/CoC/dr.json", div_round_player, scoring_settings)
st.write("### Fantasyergebnisse")
st.dataframe(dr_df, hide_index=True)

# Conference Finals
st.write("## Conference Finals")
st.write("### Tippbild")
st.image("Pictures/CC.jfif", width=500)
cf_df = ind_calculate_fantasy_points_and_sort("views/CoC/cf.json", conf_round_player, scoring_settings)
# cf_df = cf_df.groupby(["Position", "Gruppe", "Preis"]).sum("FFP").reset_index()
st.write("### Fantasyergebnisse")
st.dataframe(cf_df, hide_index=True)

# Super Bowl
st.write("## Super Bowl LIX")
st.write("### Tippbild")
st.image("Pictures/SB.jfif", width=500)
cont_sb = st.container()
# sb_df = calculate_fantasy_points("views/CoC/sb.json", super_bowl_challenge, scoring_settings)
# cont_sb.dataframe(sb_df.set_index("player_id"), hide_index=True)
