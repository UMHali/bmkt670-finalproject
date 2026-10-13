import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load database settings from .env.
load_dotenv()

required = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD"
]

missing = []

for name in required:
    if not os.getenv(name):
        missing.append(name)

if missing:
    raise ValueError(
        f"Missing database settings: {missing}"
    )

# Tables must load in dependency order.
tables = [
    "dim_team",
    "dim_date",
    "fact_game",
    "fact_game_metrics",
    "fact_weather",
    "ml_features_game_duration"
]

# Read the clean CSV files before rebuilding the database.
data = {}

for table in tables:
    filename = f"data/clean/{table}.csv"
    data[table] = pd.read_csv(filename)

# Connect to PostgreSQL.
connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = connection.cursor()

try:
    # Rebuild all project tables.
    with open("sql/schema.sql", "r") as file:
        schema = file.read()

    cursor.execute(schema)


    # Load each clean table.
    for table in tables:
        df = data[table].copy()


        # Postgres creates these SERIAL values.
        if table == "fact_game_metrics":
            if not df["metrics_id"].isna().all():
                raise ValueError(
                    "metrics_id should be blank in the CSV"
                )

            df = df.drop(
                columns=["metrics_id"]
            )


        if table == "fact_weather":
            if not df["weather_id"].isna().all():
                raise ValueError(
                    "weather_id should be blank in the CSV"
                )

            df = df.drop(
                columns=["weather_id"]
            )


        # Build the INSERT statement.
        columns = ", ".join(df.columns)

        placeholders = ", ".join(
            ["%s"] * len(df.columns)
        )

        query = (
            f"INSERT INTO {table} "
            f"({columns}) "
            f"VALUES ({placeholders})"
        )


        # Insert one row at a time.
        for row in df.itertuples(
            index=False,
            name=None
        ):
            values = []

            for value in row:
                if pd.isna(value):
                    values.append(None)
                else:
                    values.append(value)

            cursor.execute(
                query,
                values
            )


        print(
            f"Loaded {table}: {len(df)} rows"
        )

    # Save all changes only after every table loads.
    connection.commit()

    print("Database load committed.")

except Exception:
    # If something fails, undo the database changes.
    connection.rollback()
    raise

finally:
    cursor.close()
    connection.close()