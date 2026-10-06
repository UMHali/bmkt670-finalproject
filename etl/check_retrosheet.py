import pandas as pd

# Read the manually downloaded Retrosheet file.
df = pd.read_csv("data/manual/retrosheet/gameinfo.csv")

# Print the number of rows and column names.
print(f"Loaded {len(df)} rows")
print("Columns:", list(df.columns))

# Check that the columns needed for the project are present.
expected = {
    "gid",
    "visteam",
    "hometeam",
    "date",
    "starttime",
    "daynight",
    "timeofgame",
    "vruns",
    "hruns",
    "season",
    "gametype"
}

missing = expected - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {missing}")

print("All required columns are present.")