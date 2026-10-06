import os
from datetime import date, timedelta

import requests
from dotenv import load_dotenv

# Load the API key from the .env file.
load_dotenv()

api_key = os.getenv("METEOSTAT_API_KEY")

if not api_key:
    raise ValueError("METEOSTAT_API_KEY is missing from .env")

# Create the folder for the raw API responses.
os.makedirs("data/raw/meteostat", exist_ok=True)

# Set the first and last dates for the weather data.
start_date = date(2023, 1, 1)
final_date = date(2025, 12, 31)

total_rows = 0

# Pull the weather data in batches of no more than 30 days.
while start_date <= final_date:
    end_date = min(start_date + timedelta(days=29), final_date)

    url = "https://meteostat.p.rapidapi.com/point/hourly"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "meteostat.p.rapidapi.com"
    }

    params = {
        "lat": 33.800369,
        "lon": -117.882596,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "tz": "America/Los_Angeles",
        "units": "metric"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    # Save the complete API response unchanged.
    filename = (
        f"data/raw/meteostat/"
        f"meteostat_{start_date}_{end_date}.json"
    )

    with open(filename, "wb") as file:
        file.write(response.content)

    # Count the hourly rows returned by this request.
    data = response.json()
    row_count = len(data["data"])
    total_rows += row_count

    print(f"{start_date} through {end_date}: {row_count} hourly rows")

    # Move to the next 30-day period.
    start_date = end_date + timedelta(days=1)

print(f"Total hourly rows pulled: {total_rows}")