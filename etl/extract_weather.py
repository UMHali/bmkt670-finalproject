"""Reuse existing responses and fetch only missing weather batches."""
import json
import os
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def main():
    load_dotenv(ROOT / '.env')
    output = ROOT / 'data/raw/meteostat'
    output.mkdir(parents=True, exist_ok=True)
    start = date(2023, 1, 1)
    last = date(2025, 12, 31)
    total = 0
    while start <= last:
        end = min(start + timedelta(days=29), last)
        path = output / f'meteostat_{start}_{end}.json'
        if path.exists():
            # Read only: never overwrite an existing raw response.
            payload = json.loads(path.read_text())
            status = 'Reused'
        else:
            key = os.getenv('METEOSTAT_API_KEY')
            if not key:
                raise ValueError('METEOSTAT_API_KEY is missing from .env')
            response = requests.get(
                'https://meteostat.p.rapidapi.com/point/hourly',
                headers={'x-rapidapi-key': key, 'x-rapidapi-host': 'meteostat.p.rapidapi.com'},
                params={'lat': 33.800369, 'lon': -117.882596, 'start': start.isoformat(), 'end': end.isoformat(), 'tz': 'America/Los_Angeles', 'units': 'metric'},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            with path.open('xb') as file:
                file.write(response.content)
            status = 'Fetched'
        if not isinstance(payload.get('data'), list):
            raise TypeError(f'Weather response has no data list: {path.name}')
        count = len(payload['data'])
        total += count
        print(f'{status} {path.name}: {count} hourly rows')
        start = end + timedelta(days=1)
    print('Total hourly rows available:', total)


if __name__ == '__main__':
    main()
