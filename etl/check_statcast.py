import pandas as pd

# Read the manually downloaded Baseball Savant / Statcast file.
df = pd.read_csv("data/manual/statcast/laa_home_2023_2025.csv")

# Print the number of rows and column names.
print(f"Loaded {len(df)} rows")
print("Columns:", list(df.columns))

# Check that the columns needed for the project are present.
expected = {
    "game_date",
    "game_pk",
    "home_team",
    "away_team",
    "at_bat_number",
    "pitch_number",
    "game_year",
    "game_type"
}

missing = expected - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {missing}")

print("All required columns are present.")

# Check the number of unique games in the file.
print("Unique games:", df["game_pk"].nunique())

# Check the number of unique games for each year.
print("Unique games by year:")
print(df.groupby("game_year")["game_pk"].nunique())