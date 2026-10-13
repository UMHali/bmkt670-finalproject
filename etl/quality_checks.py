import os

import psycopg2
from dotenv import load_dotenv

# Load database settings from .env.
load_dotenv()

# Connect to PostgreSQL.
connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = connection.cursor()

# Quality check 1:
# No duplicate game IDs in fact_game.
cursor.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT game_id)
    FROM fact_game;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Duplicate fact_game game_ids: {count}"
)

# Quality check 2:
# No duplicate game IDs in fact_game_metrics.
cursor.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT game_id)
    FROM fact_game_metrics;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Duplicate fact_game_metrics game_ids: {count}"
)

# Quality check 3:
# No duplicate game IDs in fact_weather.
cursor.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT game_id)
    FROM fact_weather;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Duplicate fact_weather game_ids: {count}"
)

# Quality check 4:
# No duplicate game IDs in the ML feature table.
cursor.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT game_id)
    FROM ml_features_game_duration;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Duplicate ML game_ids: {count}"
)

# Quality check 5:
# Every fact_game date exists in dim_date.
cursor.execute("""
    SELECT COUNT(*)
    FROM fact_game g
    LEFT JOIN dim_date d
        ON g.date_id = d.date_id
    WHERE d.date_id IS NULL;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Game dates missing from dim_date: {count}"
)

# Quality check 6:
# Every opponent exists in dim_team.
cursor.execute("""
    SELECT COUNT(*)
    FROM fact_game g
    LEFT JOIN dim_team t
        ON g.opponent_id = t.team_id
    WHERE t.team_id IS NULL;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Game opponents missing from dim_team: {count}"
)

# Quality check 7:
# Every metrics row links to a game.
cursor.execute("""
    SELECT COUNT(*)
    FROM fact_game_metrics m
    LEFT JOIN fact_game g
        ON m.game_id = g.game_id
    WHERE g.game_id IS NULL;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Metrics rows missing parent game: {count}"
)

# Quality check 8:
# Every weather row links to a game.
cursor.execute("""
    SELECT COUNT(*)
    FROM fact_weather w
    LEFT JOIN fact_game g
        ON w.game_id = g.game_id
    WHERE g.game_id IS NULL;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Weather rows missing parent game: {count}"
)

# Quality check 9:
# Every ML row links to a historical game.
cursor.execute("""
    SELECT COUNT(*)
    FROM ml_features_game_duration m
    LEFT JOIN fact_game g
        ON m.game_id = g.game_id
    WHERE g.game_id IS NULL;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] ML rows missing parent game: {count}"
)

# Quality check 10:
# The ML target cannot be missing.
cursor.execute("""
    SELECT COUNT(*)
    FROM ml_features_game_duration
    WHERE duration_minutes IS NULL;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] ML rows with missing target: {count}"
)

# Quality check 11:
# Game duration must be above 0.
cursor.execute("""
    SELECT COUNT(*)
    FROM ml_features_game_duration
    WHERE duration_minutes <= 0;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] ML rows with nonpositive duration: {count}"
)

# Quality check 12:
# Split must be train, validate, or test.
cursor.execute("""
    SELECT COUNT(*)
    FROM ml_features_game_duration
    WHERE split IS NULL
       OR split NOT IN ('train', 'validate', 'test');
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] ML rows with invalid split: {count}"
)

# Quality check 13:
# Each season must have the correct split.
cursor.execute("""
    SELECT COUNT(*)
    FROM ml_features_game_duration
    WHERE (season = 2023 AND split <> 'train')
       OR (season = 2024 AND split <> 'validate')
       OR (season = 2025 AND split <> 'test')
       OR season NOT IN (2023, 2024, 2025);
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Season/split mismatches: {count}"
)

# Quality check 14:
# fact_game should contain all 243 historical games.
cursor.execute("""
    SELECT COUNT(*)
    FROM fact_game;
""")

count = cursor.fetchone()[0]

if count == 243:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] fact_game rows: {count} (expected 243)"
)

# Quality check 15:
# fact_game_metrics should contain all 243 games.
cursor.execute("""
    SELECT COUNT(*)
    FROM fact_game_metrics;
""")

count = cursor.fetchone()[0]

if count == 243:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] fact_game_metrics rows: {count} (expected 243)"
)

# Quality check 16:
# fact_weather should contain all 243 games.
cursor.execute("""
    SELECT COUNT(*)
    FROM fact_weather;
""")

count = cursor.fetchone()[0]

if count == 243:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] fact_weather rows: {count} (expected 243)"
)

# Quality check 17:
# The ML table should have 242 rows.
cursor.execute("""
    SELECT COUNT(*)
    FROM ml_features_game_duration;
""")

count = cursor.fetchone()[0]

if count == 242:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] ML feature rows: {count} (expected 242)"
)

# Quality check 18:
# Only the first historical game should be absent from ML.
cursor.execute("""
    SELECT COUNT(*)
    FROM fact_game g
    LEFT JOIN ml_features_game_duration m
        ON g.game_id = m.game_id
    WHERE m.game_id IS NULL
      AND g.game_id <> (
          SELECT game_id
          FROM fact_game
          ORDER BY date_id, start_time, game_id
          LIMIT 1
      );
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Unexpected historical games missing from ML: {count}"
)

# Quality check 19:
# Exactly one weekday column should equal 1 for each ML row.
cursor.execute("""
    SELECT COUNT(*)
    FROM ml_features_game_duration
    WHERE dow_monday
        + dow_tuesday
        + dow_wednesday
        + dow_thursday
        + dow_friday
        + dow_saturday
        + dow_sunday <> 1;
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Invalid weekday encodings: {count}"
)

# Quality check 20:
# The expected train/validate/test row counts should match.
cursor.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT split, COUNT(*) AS row_count
        FROM ml_features_game_duration
        GROUP BY split
    ) counts
    WHERE (split = 'train' AND row_count <> 80)
       OR (split = 'validate' AND row_count <> 81)
       OR (split = 'test' AND row_count <> 81);
""")

count = cursor.fetchone()[0]

if count == 0:
    status = "PASS"
else:
    status = "FAIL"

print(
    f"[{status}] Incorrect split row counts: {count}"
)

print(
    "Expected difference: 243 historical games "
    "minus the first 2023 game with no prior "
    "post-pitch-clock history = 242 ML rows."
)

cursor.close()
connection.close()