import glob
import json
import os

import pandas as pd

# Create the clean-data folder if it does not already exist.
os.makedirs("data/clean", exist_ok=True)

# Convert Retrosheet codes to Statcast-style code.
team_code_map = {
    "ARI": "AZ",
    "CHA": "CWS",
    "CHN": "CHC",
    "KCA": "KC",
    "LAN": "LAD",
    "NYA": "NYY",
    "NYN": "NYM",
    "SDN": "SD",
    "SFN": "SF",
    "SLN": "STL",
    "TBA": "TB",
    "WAS": "WSH",
    "OAK": "ATH",
    "ATH": "ATH"
}

# These four doubleheader games were verified using date, opponent, and historical final score.
doubleheader_map = {
    716915: "ANA202308191",
    716925: "ANA202308192",
    716890: "ANA202308231",
    716903: "ANA202308232"
}

# Retrosheet
# Read the manually downloaded Retrosheet file.
retrosheet = pd.read_csv(
    "data/manual/retrosheet/gameinfo.csv",
    low_memory=False
)

print(f"Retrosheet source rows: {len(retrosheet)}")

# Check that the columns needed for the project are present.
expected = {
    "gid",
    "date",
    "season",
    "gametype",
    "visteam",
    "hometeam",
    "starttime",
    "daynight",
    "hruns",
    "vruns",
    "timeofgame"
}

missing = expected - set(retrosheet.columns)
if missing:
    raise ValueError(f"Retrosheet missing columns: {missing}")

# Keep only 2023-2025 regular-season Angels home games.
in_window = retrosheet["season"].isin([2023, 2024, 2025])
regular = retrosheet["gametype"] == "regular"
home = retrosheet["hometeam"] == "ANA"

games = retrosheet[in_window & regular & home].copy()

print(f"Dropped outside 2023-2025: {(~in_window).sum()}")
print(
    "Dropped nonregular games within window:",
    (in_window & ~regular).sum()
)
print(
    "Dropped away games within regular window:",
    (in_window & regular & ~home).sum()
)
print(f"Rows kept: {len(games)}")
print(f"Rows dropped: {len(retrosheet) - len(games)}")

# Confirm the expected number of home games.
games_by_year = games.groupby("season").size()

print("Retrosheet home games by year:")
print(games_by_year)

if len(games) != 243:
    raise ValueError("Expected 243 Retrosheet home games")

if games_by_year.to_dict() != {2023: 81, 2024: 81, 2025: 81}:
    raise ValueError("Unexpected Retrosheet game counts by season")

# Check for missing values in fields needed for the project.
core_columns = [
    "gid",
    "date",
    "visteam",
    "starttime",
    "daynight",
    "hruns",
    "vruns",
    "timeofgame"
]

print("Retrosheet core missing counts:")
print(games[core_columns].isna().sum())

if games[core_columns].isna().sum().sum() > 0:
    raise ValueError("Retrosheet has missing core values")

# Check for duplicate game IDs.
if games["gid"].duplicated().any():
    raise ValueError("Retrosheet has duplicate game IDs")

# Rename source fields to project field names.
games = games.rename(
    columns={
        "gid": "game_id",
        "date": "date_id",
        "visteam": "opponent_id",
        "starttime": "start_time",
        "daynight": "day_night",
        "hruns": "home_runs",
        "vruns": "away_runs",
        "timeofgame": "duration_minutes"
    }
)

# Convert the date and start time into standard formats.
games["date_id"] = pd.to_datetime(
    games["date_id"].astype(str),
    format="%Y%m%d"
)

games["game_datetime"] = pd.to_datetime(
    games["date_id"].dt.strftime("%Y-%m-%d")
    + " "
    + games["start_time"],
    format="%Y-%m-%d %I:%M%p"
)

games["start_time"] = games["game_datetime"].dt.strftime("%H:%M:%S")

# Normalize opponent codes.
games["opponent_id"] = games["opponent_id"].replace(team_code_map)

# Check expected values.
if not games["day_night"].isin(["day", "night"]).all():
    raise ValueError("Unexpected day/night value")

if not (games["duration_minutes"] > 0).all():
    raise ValueError("Game duration must be above 0")

# Sort games in chronological order.
games = games.sort_values("game_datetime").reset_index(drop=True)

# Statcast
statcast_files = [
    (2023, "data/manual/statcast/laa_home_2023.csv"),
    (2024, "data/manual/statcast/laa_home_2024.csv"),
    (2025, "data/manual/statcast/laa_home_2025.csv")
]

statcast_frames = []

expected = {
    "game_date",
    "game_pk",
    "home_team",
    "away_team",
    "at_bat_number",
    "pitch_number",
    "game_year",
    "game_type",
    "inning_topbot"
}

# Read and check each annual Statcast file.
for year, filename in statcast_files:
    statcast_year = pd.read_csv(filename, low_memory=False)

    missing = expected - set(statcast_year.columns)

    if missing:
        raise ValueError(
            f"Statcast {year} missing columns: {missing}"
        )

    print(
        f"Statcast {year}: "
        f"{len(statcast_year)} rows, "
        f"{statcast_year['game_pk'].nunique()} games"
    )

    print(f"Statcast {year} core missing counts:")
    print(statcast_year[list(expected)].isna().sum())

    if statcast_year[list(expected)].isna().sum().sum() > 0:
        raise ValueError(
            f"Statcast {year} has missing core values"
        )

    if statcast_year["game_pk"].nunique() != 81:
        raise ValueError(
            f"Statcast {year} should contain 81 games"
        )

    if not statcast_year["game_year"].eq(year).all():
        raise ValueError(
            f"Unexpected game year in Statcast {year}"
        )

    if not statcast_year["home_team"].eq("LAA").all():
        raise ValueError(
            f"Unexpected home team in Statcast {year}"
        )

    if not statcast_year["game_type"].eq("R").all():
        raise ValueError(
            f"Unexpected game type in Statcast {year}"
        )

    duplicate_pitch_keys = statcast_year.duplicated(
        ["game_pk", "at_bat_number", "pitch_number"]
    ).sum()

    if duplicate_pitch_keys > 0:
        raise ValueError(
            f"Statcast {year} has duplicate pitch keys"
        )

    statcast_frames.append(statcast_year)

# Combine the three annual files in memory.
statcast = pd.concat(statcast_frames, ignore_index=True).copy()

print(f"Combined Statcast rows: {len(statcast)}")
print(
    "Combined Statcast games:",
    statcast["game_pk"].nunique()
)

if statcast["game_pk"].nunique() != 243:
    raise ValueError("Expected 243 unique Statcast games")

# Convert Statcast game date to a date field.
statcast["date_id"] = pd.to_datetime(
    statcast["game_date"]
)

# Confirm that the normalized opponent codes agree across sources.
retrosheet_codes = set(games["opponent_id"])
statcast_codes = set(statcast["away_team"])

unmatched_retrosheet = sorted(
    retrosheet_codes - statcast_codes
)

unmatched_statcast = sorted(
    statcast_codes - retrosheet_codes
)

print(
    "Unmatched Retrosheet opponent codes:",
    unmatched_retrosheet
)
print(
    "Unmatched Statcast opponent codes:",
    unmatched_statcast
)

if unmatched_retrosheet or unmatched_statcast:
    raise ValueError("Opponent codes do not match across sources")

# Create one Statcast row per game.
statcast_games = statcast[
    ["game_pk", "date_id", "away_team"]
].drop_duplicates()

statcast_games = statcast_games.rename(
    columns={"away_team": "opponent_id"}
)

if len(statcast_games) != 243:
    raise ValueError(
        "Expected 243 game-level Statcast rows"
    )

# Keep Angels batting records.
angels_batting = statcast[
    statcast["inning_topbot"] == "Bot"
].copy()

# Count unique Angels plate appearances in each game.
plate_appearances = (
    angels_batting
    .groupby("game_pk")["at_bat_number"]
    .nunique()
    .reset_index(
        name="angels_plate_appearances"
    )
)

if len(plate_appearances) != 243:
    raise ValueError(
        "One or more games have no Angels batting records"
    )

# Match Statcast games to Retrosheet
# Match ordinary games using date and normalized opponent.
ordinary_statcast = statcast_games[
    ~statcast_games["game_pk"].isin(doubleheader_map)
].copy()

ordinary_retrosheet = games[
    ~games["game_id"].isin(doubleheader_map.values())
][
    ["game_id", "date_id", "opponent_id"]
].copy()

# Date + opponent must be unique outside the approved doubleheaders.
if ordinary_statcast.duplicated(
    ["date_id", "opponent_id"]
).any():
    raise ValueError(
        "Unexpected duplicate Statcast date/opponent"
    )

if ordinary_retrosheet.duplicated(
    ["date_id", "opponent_id"]
).any():
    raise ValueError(
        "Unexpected duplicate Retrosheet date/opponent"
    )


ordinary_matches = ordinary_statcast.merge(
    ordinary_retrosheet,
    on=["date_id", "opponent_id"],
    how="left"
)

if ordinary_matches["game_id"].isna().any():
    raise ValueError(
        "One or more Statcast games did not match Retrosheet"
    )

if ordinary_matches["game_id"].duplicated().any():
    raise ValueError(
        "Duplicate ordinary game match"
    )

# Use the approved explicit mapping for the four doubleheader games.
doubleheader_games = statcast_games[
    statcast_games["game_pk"].isin(doubleheader_map)
].copy()

doubleheader_games["game_id"] = (
    doubleheader_games["game_pk"]
    .map(doubleheader_map)
)

# Confirm that the approved mapping agrees on date and opponent.
doubleheader_check = doubleheader_games.merge(
    games[
        ["game_id", "date_id", "opponent_id"]
    ],
    on="game_id",
    how="left",
    suffixes=("_statcast", "_retrosheet")
)

if len(doubleheader_check) != 4:
    raise ValueError(
        "Expected four doubleheader matches"
    )

if not doubleheader_check[
    "date_id_statcast"
].eq(
    doubleheader_check["date_id_retrosheet"]
).all():
    raise ValueError(
        "Doubleheader dates do not match"
    )

if not doubleheader_check[
    "opponent_id_statcast"
].eq(
    doubleheader_check["opponent_id_retrosheet"]
).all():
    raise ValueError(
        "Doubleheader opponents do not match"
    )

# Combine ordinary and doubleheader matches.
matched_games = pd.concat(
    [
        ordinary_matches[
            ["game_pk", "game_id"]
        ],
        doubleheader_games[
            ["game_pk", "game_id"]
        ]
    ],
    ignore_index=True
)

print(
    f"Matched games: {len(matched_games)}"
)
print(
    "Unique matched game IDs:",
    matched_games["game_id"].nunique()
)

if len(matched_games) != 243:
    raise ValueError(
        "Expected 243 matched games"
    )

if matched_games["game_id"].nunique() != 243:
    raise ValueError(
        "Matched game IDs are not unique"
    )

if set(matched_games["game_id"]) != set(games["game_id"]):
    raise ValueError(
        "Matched game IDs do not equal Retrosheet game IDs"
    )

# Build the clean game-metrics table.
fact_game_metrics = matched_games.merge(
    plate_appearances,
    on="game_pk",
    how="left"
)

if fact_game_metrics[
    "angels_plate_appearances"
].isna().any():
    raise ValueError(
        "Missing plate appearance count"
    )

fact_game_metrics[
    "angels_plate_appearances"
] = fact_game_metrics[
    "angels_plate_appearances"
].astype(int)

fact_game_metrics["metrics_id"] = pd.NA

fact_game_metrics = fact_game_metrics[
    [
        "metrics_id",
        "game_id",
        "angels_plate_appearances"
    ]
]

# Weather
weather_files = sorted(
    glob.glob("data/raw/meteostat/*.json")
)

if len(weather_files) == 0:
    raise ValueError("No Meteostat files found")


weather_rows = []

for filename in weather_files:
    with open(filename, "r") as file:
        response = json.load(file)

    weather_rows.extend(response["data"])

weather = pd.DataFrame(weather_rows)

print(
    f"Raw weather files: {len(weather_files)}"
)
print(
    f"Raw weather rows: {len(weather)}"
)

expected = {"time", "temp", "prcp", "wspd"}

missing = expected - set(weather.columns)

if missing:
    raise ValueError(
        f"Weather missing columns: {missing}"
    )

print("Raw weather missing counts:")
print(
    weather[
        ["time", "temp", "prcp", "wspd"]
    ].isna().sum()
)

# Weather timestamp is required for matching.
if weather["time"].isna().any():
    raise ValueError(
        "Weather contains missing timestamps"
    )

weather["weather_hour"] = pd.to_datetime(
    weather["time"]
)

# Match each game to the nearest local weather hour.
games["weather_hour"] = (
    games["game_datetime"].dt.round("h")
)

# None of the duplicated raw timestamps should be selected.
duplicate_weather = weather[
    weather["weather_hour"].duplicated(
        keep=False
    )
    & weather["weather_hour"].isin(
        games["weather_hour"]
    )
]

print(
    "Selected duplicate weather rows:",
    len(duplicate_weather)
)

if len(duplicate_weather) > 0:
    raise ValueError(
        "A game matched a duplicated weather timestamp"
    )

selected_weather = weather[
    weather["weather_hour"].isin(
        games["weather_hour"]
    )
].copy()

game_weather = games[
    ["game_id", "game_datetime", "weather_hour"]
].merge(
    selected_weather[
        [
            "weather_hour",
            "temp",
            "prcp",
            "wspd"
        ]
    ],
    on="weather_hour",
    how="left"
)

print("Matched weather missing counts:")
print(
    game_weather[
        ["temp", "prcp", "wspd"]
    ].isna().sum()
)

if game_weather[
    ["temp", "prcp", "wspd"]
].isna().sum().sum() > 0:
    raise ValueError(
        "One or more games have missing matched weather"
    )

game_weather["offset_minutes"] = (
    (
        game_weather["weather_hour"]
        - game_weather["game_datetime"]
    )
    .dt.total_seconds()
    / 60
)

print("Weather offsets in minutes:")
print(
    game_weather[
        "offset_minutes"
    ].value_counts().sort_index()
)

if not game_weather[
    "offset_minutes"
].abs().le(30).all():
    raise ValueError(
        "Weather match is more than 30 minutes away"
    )

fact_weather = game_weather.rename(
    columns={
        "temp": "temp_c",
        "prcp": "precip_mm",
        "wspd": "wind_speed_kmh"
    }
)

fact_weather["weather_id"] = pd.NA

fact_weather = fact_weather[
    [
        "weather_id",
        "game_id",
        "temp_c",
        "precip_mm",
        "wind_speed_kmh"
    ]
]

# Dimension and fact tables
dim_team = pd.DataFrame(
    {
        "team_id":
        sorted(games["opponent_id"].unique())
    }
)

dim_date = games[
    ["date_id", "season"]
].drop_duplicates().copy()

dim_date["day_of_week"] = (
    dim_date["date_id"].dt.day_name()
)

dim_date["month"] = (
    dim_date["date_id"].dt.month
)

dim_date["is_weekend"] = (
    dim_date["date_id"].dt.dayofweek >= 5
)

dim_date = dim_date.sort_values(
    "date_id"
)

fact_game = games[
    [
        "game_id",
        "date_id",
        "opponent_id",
        "start_time",
        "day_night",
        "home_runs",
        "away_runs",
        "duration_minutes"
    ]
].copy()

# ML feature table
# Start with the historical game rows
ml = games.copy()

# Add the date features
ml = ml.merge(
    dim_date[
        [
            "date_id",
            "month",
            "is_weekend"
        ]
    ],
    on="date_id",
    how="left"
)

# Add historical plate appearances
ml = ml.merge(
    fact_game_metrics[
        [
            "game_id",
            "angels_plate_appearances"
        ]
    ],
    on="game_id",
    how="left"
)

# Add weather
ml = ml.merge(
    fact_weather[
        [
            "game_id",
            "temp_c",
            "precip_mm",
            "wind_speed_kmh"
        ]
    ],
    on="game_id",
    how="left"
)

if len(ml) != 243:
    raise ValueError(
        "ML joins changed the number of historical games"
    )

ml = ml.sort_values(
    "game_datetime"
).reset_index(drop=True)

# Create simple game-time features
ml["start_hour"] = (
    ml["game_datetime"].dt.hour
)

ml["is_weekend"] = (
    ml["is_weekend"].astype(int)
)

ml["is_night"] = (
    (ml["day_night"] == "night").astype(int)
)

# Turn day of week into 0/1 columns
weekdays = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
]

for number, day in enumerate(weekdays):
    ml["dow_" + day] = (
        (
            ml["date_id"].dt.dayofweek
            == number
        )
        .astype(int)
    )

# Use only earlier games when calculating rolling features.
# shift(1) makes sure the current game is not included.
ml["rolling_avg_duration_prev5"] = (
    ml["duration_minutes"]
    .shift(1)
    .rolling(5, min_periods=1)
    .mean()
)

total_runs = (
    ml["home_runs"]
    + ml["away_runs"]
)

ml["rolling_avg_total_runs_prev5"] = (
    total_runs
    .shift(1)
    .rolling(5, min_periods=1)
    .mean()
)

ml[
    "rolling_avg_plate_appearances_prev5"
] = (
    ml["angels_plate_appearances"]
    .shift(1)
    .rolling(5, min_periods=1)
    .mean()
)

# Calculate days since the previous home game.
ml["days_since_last_home_game"] = (
    ml["date_id"].diff().dt.days
)

# Create the time-based split.
ml["split"] = ml["season"].map(
    {
        2023: "train",
        2024: "validate",
        2025: "test"
    }
)

ml_columns = [
    "game_id",
    "date_id",
    "season",
    "opponent_id",
    "month",
    "start_hour",
    "is_weekend",
    "is_night",
    "dow_monday",
    "dow_tuesday",
    "dow_wednesday",
    "dow_thursday",
    "dow_friday",
    "dow_saturday",
    "dow_sunday",
    "temp_c",
    "precip_mm",
    "wind_speed_kmh",
    "rolling_avg_duration_prev5",
    "rolling_avg_total_runs_prev5",
    "rolling_avg_plate_appearances_prev5",
    "days_since_last_home_game",
    "duration_minutes",
    "split"
]

print("ML missing values before first-row removal:")
print(ml[ml_columns].isna().sum())

# The first 2023 game has no earlier post-pitch-clock history.
derived_columns = [
    "rolling_avg_duration_prev5",
    "rolling_avg_total_runs_prev5",
    "rolling_avg_plate_appearances_prev5",
    "days_since_last_home_game"
]

for column in derived_columns:
    if ml[column].isna().sum() != 1:
        raise ValueError(
            f"Unexpected missing values in {column}"
        )

if ml.iloc[1:][derived_columns].isna().any().any():
    raise ValueError(
        "A game other than the first has missing history"
    )

removed_game_id = ml.iloc[0]["game_id"]

ml_features_game_duration = (
    ml.iloc[1:][ml_columns].copy()
)

print(
    "ML rows removed: "
    f"1 ({removed_game_id}); "
    "no prior post-pitch-clock home-game history"
)

if len(ml_features_game_duration) != 242:
    raise ValueError(
        "Expected 242 ML rows"
    )

if ml_features_game_duration.isna().any().any():
    raise ValueError(
        "Final ML table contains missing values"
    )

split_counts = (
    ml_features_game_duration
    .groupby("split")
    .size()
    .to_dict()
)

print("ML split counts:", split_counts)

if split_counts != {
    "train": 80,
    "validate": 81,
    "test": 81
}:
    raise ValueError(
        "Unexpected ML split counts"
    )

# Save clean table
print(
    f"dim_team: {len(dim_team)} rows"
)
print(
    f"dim_date: {len(dim_date)} rows"
)
print(
    f"fact_game: {len(fact_game)} rows"
)
print(
    "fact_game_metrics:",
    len(fact_game_metrics),
    "rows"
)
print(
    f"fact_weather: {len(fact_weather)} rows"
)
print(
    "ml_features_game_duration:",
    len(ml_features_game_duration),
    "rows"
)

dim_team.to_csv(
    "data/clean/dim_team.csv",
    index=False
)

dim_date.to_csv(
    "data/clean/dim_date.csv",
    index=False,
    date_format="%Y-%m-%d"
)

fact_game.to_csv(
    "data/clean/fact_game.csv",
    index=False,
    date_format="%Y-%m-%d"
)

fact_game_metrics.to_csv(
    "data/clean/fact_game_metrics.csv",
    index=False
)

fact_weather.to_csv(
    "data/clean/fact_weather.csv",
    index=False
)

ml_features_game_duration.to_csv(
    "data/clean/ml_features_game_duration.csv",
    index=False,
    date_format="%Y-%m-%d"
)

print("Transform complete.")