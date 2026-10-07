# Los Angeles Angels Home Game Duration Prediction

## Business Question
How many minutes should Los Angeles Angels game-day operations expect an upcoming home game at Angel Stadium to last?

## Target Variable
Game duration in minutes.

## Prediction Unit
One row in my future ML feature table = one Los Angeles Angels home game.

## Data Sources
| Source | What it provides | Access |
| Retrosheet | Game information including date, opponent, start time, scores, and game duration | Manual CSV download from https://www.retrosheet.org/downloads/csvteams.html, downloaded October 6, 2026. Selected the Angels team download and saved `gameinfo.csv` unchanged in `data/manual/retrosheet/`. |
| Baseball Savant / Statcast | Pitch-level Angels home-game data used for historical game pace measures | Manual CSV download from https://baseballsavant.mlb.com/statcast_search, downloaded October 6, 2026. Filters: Player Type = Batter; Season Type = Regular Season; Seasons = 2023, 2024, 2025; Team = Angels; Home or Away = Home; Group By = Player & Event. Saved unchanged as `data/manual/statcast/laa_home_2023_2025.csv`. |
| Meteostat | Historical hourly temperature, precipitation, and wind at Angel Stadium | API using `etl/extract_weather.py`; raw JSON responses saved in `data/raw/meteostat/`. |

## How to Run
1. Create and activate a virtual environment.
2. Install packages:
   `pip install -r requirements.txt`
3. Create a `.env` file with your API key and database connection information.
4. Run the source scripts:
   `python etl/check_retrosheet.py`
   `python etl/check_statcast.py`
   `python etl/extract_weather.py`
5. Build the database by running `sql/schema.sql` in pgAdmin.
6. Confirm the database tables were created:
   `python db_check.py`

## AI Usage
I used OpenAI Codex through Visual Studio Code as the coding agent for the Database Design & Setup portion of this project.

It created `etl/check_retrosheet.py` to read the Retrosheet `gameinfo.csv` file, print the row count and column names, and check that the required fields were present. It also created `etl/check_statcast.py` to read the Baseball Savant / Statcast `laa_home_2023_2025.csv` file, print the row count and column names, check the required fields, count unique games, and confirm the number of games represented for each season.

Codex created `etl/extract_weather.py` to make the Meteostat API requests. The script reads the API key from the `.env` file, requests hourly weather data in date ranges that follow the API request limit, saves each raw JSON response unchanged in `data/raw/meteostat/`, and prints the number of weather rows returned. 

Codex wrote the PostgreSQL syntax in `sql/schema.sql` using the database structure I provided. It created the `CREATE TABLE`, primary key, foreign key, data type, table comment, and `DROP TABLE IF EXISTS ... CASCADE` statements needed to build the dimension and fact tables. It did not load data into the database or create the ML feature table.

Codex created `docs/field_sources.md` using the database fields and source relationships provided for the project.

Codex also helped troubleshoot the PostgreSQL `libpq` library-path issue on my Mac, ran the Retrosheet and Statcast source-check scripts, and ran the Meteostat extraction script.

IMPORTANT NOTE: I reviewed and verified all AI-generated work before using it. I made several changes to simplify the code, keep it consistent with methods and concepts used in this course and other coursework, and make sure I understood what each part of the code was doing because some of it was super complicated stuff I had never seen before so I rewrote it.
