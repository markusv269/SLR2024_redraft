import streamlit as st
from sleeper_wrapper import User
from utils import AIRTABLE_API_KEY, BASE_ID 
import datetime, time
from datetime import datetime
import requests
import json

AIRTABLE_API_KEY = AIRTABLE_API_KEY
BASE_ID = BASE_ID
TABLE_NAME = "SLR2025"

def save_to_airtable(sleeper, discord, commish, mitspieler):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "records": [
            {"fields": {"Sleeper": sleeper, "Discord": discord, "Commish": commish, "Mitspieler": ", ".join(map(str, mitspieler)), "Anmeldezeit": datetime.now().isoformat()}}
             ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Debugging-Ausgabe
    if response.status_code != 200:
        print(f"Fehler: {response.status_code}")
        print(response.text)

    return response.status_code == 200

@st.cache_data
def get_user_id(username):
    """Cached function to fetch Sleeper user ID."""
    try:
        user = User(username)
        return user.get_user_id() is not None
    except Exception:
        return False

st.write("# SLR2025 Anmeldung")
st.markdown('''
    Dieses Formular dient zur Anmeldung bei den allseits beliebten Stoned Lack Redraft Ligen. 
    Gespielt wird auf  Sleeper.
    Die Zuteilung zu einer bestimmten Liga erfolgt via Auslosung Ende August 2025 im Live Stream von Stoned Lack!

    Bitte tragt euch hier mit euren Kontakt-Daten ein, mit denen euch euer Commissioner nach der Auslosung in die Liga einladen kann. 
    Bitte merkt euch wann die Auslosung ist, und dass ihr danach dann eine Einladung erhaltet  und schaut regelmäßig in Sleeper / Discord, damit die Liga zügig zustande kommt und der Draft beginnen kann.

    Bitte achtet auf die genaue Schreibweise eurer Namen in Sleeper und Discord!

    Eine Liga ist nichts ohne einen guten Commissioner! 
    Wir würden uns sehr freuen, wenn sich ausreichend Freiwillige melden würden, in ihrer Liga die Rolle des Commish zu übernehmen. 
    Erfahrung ist nicht unbedingt nötig, ihr bekommt gerne ausreichend Hilfestellung im Discord der Stoned Lack Army.

    Wir freuen uns auf zahlreiche Teilnahme!

    Let's go! 

    _Die hier erhobenen Daten werden nur zum Zwecke und für die Dauer der Durchführung der Stoned Lack Redraft Ligen gespeichert. Durch Ausfüllen des Formulars erklärst du dich damit einverstanden, dass diese Daten zu diesem Zweck verwendet werden dürfen. Eine Auskunft über diese Daten ist jederzeit möglich._''')
st.write("## Melde Dich hier für die StonedLack Redraftligen 2025 an")
commish = st.checkbox("Ich übernehme einen Commish-Posten!")
mitspieler = st.checkbox("Ich möchte mit jemandem zusammenspielen")

with st.form("Anmeldung SLR 2025"):
    sleeper_name = st.text_input("Dein Sleeper-Name", key="sleeper")
    discord_name = st.text_input("Dein Discord-Name", key="discord")

    mitspieler_names = []
    if mitspieler:
        st.write("Trage bis zu 3 Mitspieler ein:")
        col1, col2, col3 = st.columns(3)
        mitspieler_inputs = [
            col1.text_input("Mitspieler 1"),
            col2.text_input("Mitspieler 2"),
            col3.text_input("Mitspieler 3")
        ]
        mitspieler_names = [name.strip() for name in mitspieler_inputs if name.strip()]
    
    submitted = st.form_submit_button("Anmelden!")

    if submitted:
        errors = []
        
        if not sleeper_name:
            errors.append("Bitte gib deinen Sleeper-Namen an.")
        elif not get_user_id(sleeper_name):
            errors.append(f"Sleeper-Name '{sleeper_name}' nicht gefunden. Bitte überprüfe deine Eingabe.")
        
        if not discord_name:
            errors.append("Bitte gib deinen Discord-Namen an.")
        
        for name in mitspieler_names:
            if not get_user_id(name):
                errors.append(f"Mitspieler '{name}' nicht gefunden. Bitte überprüfe den Sleeper-Namen.")
        
        if errors:
            st.error("\n".join(errors))
        else:
            st.success("Anmeldung erfolgreich!")
            save_to_airtable(sleeper_name, discord_name, commish, mitspieler=mitspieler_names)