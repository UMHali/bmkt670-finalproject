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
This project uses only the 2023–2025 regular seasons because the pitch clock began in 2023. No pre-2023 games are used for training or historical features. The chronological split is 2023 = train, 2024 = validate, and 2025 = test.

The three annual Statcast files replaced the combined 25,000-row export after validation found completeness concerns. The combined export is not used. Only Angels plate appearances are counted; delivered-pitch totals are not calculated because automatic records make that count ambiguous.

Approved team codes are normalized to Statcast abbreviations, including OAK and ATH → ATH. Four verified doubleheader mappings resolve repeated date/opponent pairs. See `docs/field_sources.md`.

Rolling averages use `shift(1)` before a five-game rolling window, with `min_periods=1` to use available prior history. Doubleheaders are ordered by start time, and history continues across seasons. Current-game scores and batting totals are excluded from ML predictors. Only the first home game is removed from ML for lack of prior post-pitch-clock history: 243 historical games, 242 ML rows.

Weather matches the nearest local hourly observation within 30 minutes. Raw precipitation gaps are unchanged because none is selected for a game. Historical observed weather and Retrosheet start times should be reviewed for availability before deploying an upcoming-game model; forecasts are needed for future weather. Missing-value decisions are in `docs/missing_data.md`.

## How to Run
From the project folder, activate your environment and install dependencies if needed:

```sh
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set `METEOSTAT_API_KEY`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` in your private `.env` file.

```sh
python run_pipeline.py
```

On this Mac, if psycopg2 reports a missing `libpq.5.dylib`, use:

```sh
DYLD_LIBRARY_PATH=/Library/PostgreSQL/18/lib python run_pipeline.py
```

The pipeline runs source checks, weather extraction, transform, load, and quality checks in that order. Existing weather JSON files are read and reused; only missing batches are fetched. Source files are never overwritten. Clean outputs are written to `data/clean/`.

**The load step executes `sql/schema.sql`, dropping and rebuilding the project tables and their dependent objects.** Inserts and the rebuild share a transaction, which rolls back if loading fails. Quality checks print PASS or FAIL for every check without stopping on data-check failures. A script crash stops the pipeline; `Pipeline finished.` appears only when all scripts complete.

Run any individual step with `python etl/transform.py`, `python etl/load.py`, or `python etl/quality_checks.py`. `python db_check.py` lists public tables.

## AI Usage
I used OpenAI Codex through Visual Studio Code as a coding agent for portions of this final project, including the Database Design & Setup work and the Transform, Load, ML Feature Table, and Data Quality work.

Codex helped create the initial source-check scripts for Retrosheet and Baseball Savant / Statcast. These scripts read the manually downloaded files, print row counts and column names, check that required fields are present, and validate the number of games represented in each season.

Codex helped create `etl/extract_weather.py` for the Meteostat API. The script reads the API key from the private `.env` file, requests hourly weather data in date ranges that follow the API request limit, saves the raw JSON responses in `data/raw/meteostat/`, and prints the number of weather rows returned.

Codex helped with the PostgreSQL syntax in `sql/schema.sql` using the database design and field decisions I provided. It also helped create the initial versions of `etl/transform.py`, `etl/load.py`, `etl/quality_checks.py`, and `run_pipeline.py`, as well as updates to `docs/field_sources.md` and `docs/missing_data.md`.

During source validation, Codex identified problems that required additional review, including the capped combined Statcast export, doubleheader matching, differences in team abbreviations, automatic ball and automatic strike records, and missing values in the raw weather data. I reviewed these findings and made the project decisions about how each issue should be handled.

I reviewed every AI-generated file and the code it contained. I revised code when it used approaches I had not learned or could not explain, and I changed it to use methods consistent with this course or other coursework I understand. I then ran and checked the final scripts and pipeline myself and reviewed the resulting row counts, missing values, joins, rolling features, database loads, and quality checks.