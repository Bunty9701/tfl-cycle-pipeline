import requests
import pandas as pd
from datetime import datetime
import os

TFL_APP_KEY = os.environ.get("TFL_APP_KEY")

def parse_station(station):
    props = {p['key']: p['value'] for p in station['additionalProperties']}
    return {
        'station_id': station['id'],
        'station_name': station['commonName'],
        'lat': station['lat'],
        'lon': station['lon'],
        'bikes_available': int(props.get('NbBikes', 0)),
        'empty_docks': int(props.get('NbEmptyDocks', 0)),
        'total_docks': int(props.get('NbDocks', 0)),
        'pulled_at': datetime.utcnow().isoformat()
    }

def pull_and_save_bikepoint_data():
    url = "https://api.tfl.gov.uk/BikePoint"
    params = {"app_key": TFL_APP_KEY}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("API call failed:", response.status_code)
        return

    data = response.json()
    parsed_data = [parse_station(s) for s in data]
    df = pd.DataFrame(parsed_data)

    os.makedirs("data", exist_ok=True)
    filename = f"data/bikepoint_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(filename, index=False)
    print(f"Pulled {len(df)} stations -> saved to {filename}")

if __name__ == "__main__":
    pull_and_save_bikepoint_data()
  
