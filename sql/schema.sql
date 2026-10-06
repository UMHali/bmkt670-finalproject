-- CASCADE removes dependent objects; rerunning also removes existing table data.
DROP TABLE IF EXISTS fact_weather CASCADE;
DROP TABLE IF EXISTS fact_game_metrics CASCADE;
DROP TABLE IF EXISTS fact_game CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;

-- One row per MLB team used as an Angels opponent.
CREATE TABLE dim_team (
    team_id TEXT PRIMARY KEY,
    team_name TEXT NOT NULL
);

-- One row per game date in the project.
CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    season INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    month INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- One row per Los Angeles Angels home game.
CREATE TABLE fact_game (
    game_id TEXT PRIMARY KEY,
    date_id DATE NOT NULL REFERENCES dim_date(date_id),
    opponent_id TEXT NOT NULL REFERENCES dim_team(team_id),
    start_time TIME,
    day_night TEXT,
    home_runs INTEGER,
    away_runs INTEGER,
    duration_minutes INTEGER
);

-- Historical Angels batting pace measures for one home game.
CREATE TABLE fact_game_metrics (
    metrics_id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL UNIQUE REFERENCES fact_game(game_id),
    angels_pitches_seen INTEGER,
    angels_plate_appearances INTEGER
);

-- Weather at the hour nearest the start of one home game.
CREATE TABLE fact_weather (
    weather_id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL UNIQUE REFERENCES fact_game(game_id),
    temp_c NUMERIC(5,2),
    precip_mm NUMERIC(6,2),
    wind_speed_kmh NUMERIC(6,2)
);
