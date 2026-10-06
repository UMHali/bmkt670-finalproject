# bmkt670-finalproject
# Los Angeles Angels Home Game Duration Prediction

## Business Question
How many minutes should Los Angeles Angels game-day operations expect an upcoming home game at Angel Stadium to last?

## Target Variable
Game duration in minutes.

## Prediction Unit
One row in my ML feature table = one Los Angeles Angels home game.

## Data Sources
Retrosheet
Baseball Savant / Statcast
Meteostat

## How to Run
1. Create and activate a virtual environment.
2. Install packages: pip install -r requirements.txt
3. Create a .env file with METEOSTAT_API_KEY and database connection information.
4. Pull or check the data by running each script in etl/.
5. Build the database by running sql/schema.sql in pgAdmin.
6. Confirm the database connection by running python db_check.py.

## AI Usage
I used OpenAI Codex through Visual Studio Code to help create routine project files, extraction/check scripts, SQL syntax, and documentation formatting. I reviewed and ran the AI-generated code myself and used Semgrep and Ruff to check the project. The business question, target variable, table design, feature choices, and interpretation remain my decisions.