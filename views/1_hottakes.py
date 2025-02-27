import streamlit as st
import pandas as pd
import os

CSV_FILE = "aussagen.csv"

def load_data():
    """Lädt bestehende Daten aus der CSV-Datei."""
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["Quelle", "Aussage"])

def save_data(option, option_wo, text, date):
    """Speichert die Eingaben in der CSV-Datei."""
    df = load_data()
    new_entry = pd.DataFrame([[option, option_wo, text, date]], columns=["Quelle", "Wo", "Aussage", "Datum"])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def main():
    st.title("Hot Takes Sammlung")
    st.write("Wieder mal ein Hot Take von Stoni oder Lack? Hier ist der richtige Platz, um alle Aussagen abzuspeichern.")
    st.write("Sammelt hier alle Hot Takes, um sie den beiden später vorhalten zu können oder ihr Fantasy-Genie-Dasein zu bekunden!")

    with st.form("quote_form"):
        option = st.radio("Wähle eine Option:", ["Stoni sagt", "Lack sagt"])
        option_wo = st.radio("Wo wurde die Aussage gemacht?", ["Montags-Podcast", "Start&Sit", "Reel/Social Media", "Discord", "Sonstige"])
        text = st.text_area("Gib deinen Text ein:")
        date = st.date_input("Wähle Datum der Aussage:", format="DD.MM.YYYY")
        submitted = st.form_submit_button("Absenden")

        if submitted and text.strip():
            save_data(option, option_wo, text, date)
            st.success(f"**{option}:** {text} am {date}")
        else:
            st.error("Bitte Text eingeben!")

    # Lade und zeige die gespeicherten Aussagen
    df = load_data()
    st.subheader("Gespeicherte Aussagen")
    st.table(df.set_index("Datum"))

main()
