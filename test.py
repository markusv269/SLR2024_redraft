import requests
from utils import AIRTABLE_API_KEY, BASE_ID
TABLE_NAME = "SLR2025"

def get_airtable_fields():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?maxRecords=1"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "records" in data and data["records"]:
            fields = data["records"][0]["fields"].keys()
            print("Verfügbare Spalten in Airtable:", list(fields))
        else:
            print("⚠️ Keine Einträge gefunden. Erstelle manuell einen Dummy-Eintrag in Airtable.")
    else:
        print(f"❌ Fehler {response.status_code}: {response.text}")

# Aufruf der Funktion
get_airtable_fields()