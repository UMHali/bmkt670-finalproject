import pandas as pd

files = [
    "data/manual/statcast/laa_home_2023.csv",
    "data/manual/statcast/laa_home_2024.csv",
    "data/manual/statcast/laa_home_2025.csv"
]

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

total_rows = 0
total_games = 0

for file in files:

    # Read the manually downloaded Baseball Savant / Statcast file.
    df = pd.read_csv(file)

    # Print the number of rows and column names.
    print(f"\nFile: {file}")
    print(f"Loaded {len(df)} rows")
    print("Columns:", list(df.columns))

    missing = expected - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    print("All required columns are present.")

    # Check the number of unique games in the file.
    games = df["game_pk"].nunique()
    print("Unique games:", games)

    # Check the number of unique games for each year.
    print("Unique games by year:")
    print(df.groupby("game_year")["game_pk"].nunique())

    total_rows += len(df)
    total_games += games

print(f"\nTotal rows: {total_rows}")
print(f"Total games: {total_games}")