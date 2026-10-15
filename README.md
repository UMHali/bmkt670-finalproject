# Los Angeles Angels Home Game Duration Prediction

## Business Question
How many minutes should Los Angeles Angels game-day operations expect an upcoming home game at Angel Stadium to last?

## Target Variable
`duration_minutes`: game duration in minutes.

## Prediction Unit
One row in my ML feature table = one Los Angeles Angels home game.

## Data Sources
| Source | What it provides | Access |
|---|---|---|
| Retrosheet | Game information including date, opponent, start time, scores, and game duration | Manual CSV download from https://www.retrosheet.org/downloads/csvteams.html, downloaded October 6, 2026. Selected the Angels team download and saved `gameinfo.csv` unchanged in `data/manual/retrosheet/`. |
| Baseball Savant / Statcast | Pitch-level Angels home-game data used for historical game pace measures | Manual CSV downloads from https://baseballsavant.mlb.com/statcast_search, downloaded October 13, 2026. Filters: Player Type = Batter; Season Type = Regular Season; Team = LAA; Home or Away = Home; Group By = Player & Event; one season selected per file. Saved unchanged as `data/manual/statcast/laa_home_2023.csv`, `data/manual/statcast/laa_home_2024.csv`, and `data/manual/statcast/laa_home_2025.csv`. |
| Meteostat | Historical hourly temperature, precipitation, and wind at Angel Stadium | API using `etl/extract_weather.py`; raw JSON responses saved in `data/raw/meteostat/`. |

## Data Window and Features
This project uses the 2023–2025 regular seasons. I left out pre-2023 games because the pitch clock began in 2023, so earlier game durations were produced under a different timing environment. The time split is 2023 = train, 2024 = validate, and 2025 = test.

The historical data contains 243 Angels home games. The ML feature table contains 242 rows because the first 2023 home game has no earlier post-pitch-clock home-game history for the rolling features. Rolling features use only earlier games, so the current game's results are not included in its own predictors.

Statcast is stored as one file per season. Angels plate appearances are used as a historical game-pacing measure. Delivered-pitch totals are not used because automatic ball and automatic strike records make that count unclear. Team abbreviations are standardized across sources, and the four doubleheaders are matched to the correct game IDs.

Weather is matched to the nearest local hourly observation within 30 minutes of the game start time. No selected game weather rows are missing. Missing-data decisions are documented in `docs/missing_data.md`, and field sources and definitions are documented in `docs/field_sources.md`.

## How to Run
1. Create and activate a virtual environment
2. Install packages: `pip install -r requirements.txt`
3. Create a `.env` file with the Meteostat API key and database connection information.
4. Run the full pipeline: `python run_pipeline.py`
5. Review the row counts and PASS/FAIL quality checks. A successful run ends with `Pipeline finished.`
6. Confirm the database tables were created: `python db_check.py`

## AI Usage
I used OpenAI Codex through Visual Studio Code as a coding agent for portions of this final project, including the Database Design & Setup work and the Transform, Load, ML Feature Table, and Data Quality work.

Codex helped create the initial source-check scripts for Retrosheet and Baseball Savant / Statcast. These scripts read the manually downloaded files, print row counts and column names, check that required fields are present, and validate the number of games represented in each season.

Codex helped create `etl/extract_weather.py` for the Meteostat API. The script reads the API key from the private `.env` file, requests hourly weather data in date ranges that follow the API request limit, saves the raw JSON responses in `data/raw/meteostat/`, and prints the number of weather rows returned.

Codex helped with the PostgreSQL syntax in `sql/schema.sql` using the database design and field decisions I provided. It also helped create the initial versions of `etl/transform.py`, `etl/load.py`, `etl/quality_checks.py`, and `run_pipeline.py`, as well as updates to `docs/field_sources.md` and `docs/missing_data.md`.

During source validation, Codex identified problems that required additional review, including the capped combined Statcast export, doubleheader matching, differences in team abbreviations, automatic ball and automatic strike records, and missing values in the raw weather data. I reviewed these findings and made the project decisions about how each issue should be handled.

I reviewed every AI-generated file and the code it contained. I revised code when it used approaches I had not learned or could not explain, and I changed it to use methods consistent with this course or other coursework I understand. I then ran and checked the final scripts and pipeline myself and reviewed the resulting row counts, missing values, joins, rolling features, database loads, and quality checks.