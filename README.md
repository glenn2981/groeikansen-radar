# Groeikansen Radar — eerste prototype

## Wat zit erin?
- Dashboard met brede markt-ETF-indicatoren
- Aandelen vergelijken op koersontwikkeling en beschikbare fundamentals
- Wereld-/sectoroverzicht via ETF-koersen en volume
- Openbare institutionele houdersgegevens waar beschikbaar
- CSV-export

## Belangrijke beperkingen
- Gegevens via Yahoo Finance/yfinance kunnen vertraagd, onvolledig of tijdelijk niet beschikbaar zijn.
- ETF-koersbewegingen en volume zijn geen exacte meting van netto geldinstroom.
- Institutionele posities zijn gerapporteerd en niet live.
- Dit is geen beleggingsadvies.

## Online zetten met GitHub + Streamlit Community Cloud
1. Maak een nieuwe GitHub-repository aan, bijvoorbeeld `groeikansen-radar`.
2. Upload `app.py`, `requirements.txt` en `README.md` naar de repository.
3. Ga naar https://share.streamlit.io/ en log in met GitHub.
4. Kies **Create app** en selecteer je repository, branch `main` en bestand `app.py`.
5. Klik op **Deploy**. De eerste build kan een paar minuten duren.

Gebruik geen wachtwoorden of persoonlijke API-sleutels in `app.py`. Als we later een betaalde gegevensbron aansluiten, zetten we sleutels veilig in Streamlit Secrets.
