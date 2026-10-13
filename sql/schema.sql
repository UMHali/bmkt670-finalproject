-- Remove old tables so the schema can be run again.
DROP TABLE IF EXISTS ml_features_game_duration CASCADE;
DROP TABLE IF EXISTS fact_weather CASCADE;
DROP TABLE IF EXISTS fact_game_metrics CASCADE;
DROP TABLE IF EXISTS fact_game CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;

-- One row per MLB team used as an Angels opponent.
CREATE TABLE dim_team (
    team_id TEXT PRIMARY KEY
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

-- One row of historical Angels batting information per home game.
CREATE TABLE fact_game_metrics (
    metrics_id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL UNIQUE REFERENCES fact_game(game_id),
    angels_plate_appearances INTEGER
);

-- One row of weather information per Angels home game.
CREATE TABLE fact_weather (
    weather_id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL UNIQUE REFERENCES fact_game(game_id),
    temp_c NUMERIC(5,2),
    precip_mm NUMERIC(6,2),
    wind_speed_kmh NUMERIC(6,2)
);

-- One row per eligible Angels home game used by the ML model.
CREATE TABLE ml_features_game_duration (
    game_id TEXT PRIMARY KEY REFERENCES fact_game(game_id),
    date_id DATE NOT NULL REFERENCES dim_date(date_id),
    season INTEGER NOT NULL,
    opponent_id TEXT NOT NULL REFERENCES dim_team(team_id),
    month INTEGER NOT NULL,
    start_hour INTEGER NOT NULL,
    is_weekend INTEGER NOT NULL,
    is_night INTEGER NOT NULL,
    dow_monday INTEGER NOT NULL,
    dow_tuesday INTEGER NOT NULL,
    dow_wednesday INTEGER NOT NULL,
    dow_thursday INTEGER NOT NULL,
    dow_friday INTEGER NOT NULL,
    dow_saturday INTEGER NOT NULL,
    dow_sunday INTEGER NOT NULL,
    temp_c NUMERIC(5,2),
    precip_mm NUMERIC(6,2),
    wind_speed_kmh NUMERIC(6,2),
    rolling_avg_duration_prev5 DOUBLE PRECISION,
    rolling_avg_total_runs_prev5 DOUBLE PRECISION,
    rolling_avg_plate_appearances_prev5 DOUBLE PRECISION,
    days_since_last_home_game INTEGER,
    duration_minutes INTEGER NOT NULL,
    split TEXT NOT NULL
        CHECK (split IN ('train', 'validate', 'test'))
);