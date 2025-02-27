import streamlit as st
import pandas as pd
import requests
import json

# Airtable Konfiguration
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_NAME = st.secrets["airtable"]["table_name"]

# Funktion zum Speichern in Airtable
def save_to_airtable(option, text):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"records": [{"fields": {"Quelle": option, "Aussage": text}}]}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.status_code == 200

# Funktion zum Laden der Daten aus Airtable
def load_from_airtable():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        records = response.json().get("records", [])
        return pd.DataFrame([rec["fields"] for rec in records])
    return pd.DataFrame(columns=["Quelle", "Aussage"])

def main():
    st.title("Zitate-Formular mit Airtable")

    with st.form("quote_form"):
        option = st.radio("Wähle eine Option:", ["Stoni sagt", "Lack sagt"])
        text = st.text_area("Gib deinen Text ein:")
        submitted = st.form_submit_button("Absenden")

        if submitted and text.strip():
            if save_to_airtable(option, text):
                st.success(f"**{option}:** {text}")
            else:
                st.error("Fehler beim Speichern in Airtable!")

    # Lade und zeige gespeicherte Aussagen
    df = load_from_airtable()
    st.subheader("Gespeicherte Aussagen")
    st.dataframe(df)

main()