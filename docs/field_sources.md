# Field Sources
The prediction unit for this project is one Los Angeles Angels home game. The table below shows where every field in the database comes from and what it will be used for.

| Table | Field | Comes from | How | Used for |
|---|---|---|---|---|
| dim_team | team_id | Retrosheet | Use `visteam` for an Angels home game | Key: links each game to its opponent |
| dim_team | team_name | Calculated in Python | Map the Retrosheet team code to the full MLB team name using a lookup dictionary | Dashboard shows readable opponent name |
| dim_date | date_id | Retrosheet | Use `date` and convert it to a date type | Key: links each game to its date |
| dim_date | season | Retrosheet | Use `season` | Feature; also groups games by season |
| dim_date | day_of_week | Calculated in Python | pandas, from `date_id` | Feature |
| dim_date | month | Calculated in Python | pandas, from `date_id` | Feature |
| dim_date | is_weekend | Calculated in Python | Saturday or Sunday = True; otherwise False | Feature |
| fact_game | game_id | Retrosheet | Use `gid` | Key: one ID per game |
| fact_game | date_id | Retrosheet | Use `date` | Key: links to `dim_date` |
| fact_game | opponent_id | Retrosheet | Use `visteam` for Angels home games | Key: links to `dim_team` |
| fact_game | start_time | Retrosheet | Use `starttime` | Feature; also matches weather to game start |
| fact_game | day_night | Retrosheet | Use `daynight` | Feature |
| fact_game | home_runs | Retrosheet | Use `hruns` | Input to a future lagged or rolling feature |
| fact_game | away_runs | Retrosheet | Use `vruns` | Input to a future lagged or rolling feature |
| fact_game | duration_minutes | Retrosheet | Use `timeofgame` | Training the model: past game duration target |
| fact_game_metrics | metrics_id | Created by Postgres | Auto-numbered with `SERIAL` | Key: primary key |
| fact_game_metrics | game_id | Matched in Python | Match Statcast games to Retrosheet games using date and teams; store the matching Retrosheet `gid` | Key: links to `fact_game` |
| fact_game_metrics | angels_pitches_seen | Calculated in Python | Count Angels pitch records within each `game_pk` after validating the pitch-level data | Input to a future lagged or rolling feature |
| fact_game_metrics | angels_plate_appearances | Calculated in Python | Count unique `at_bat_number` values within each `game_pk` | Input to a future lagged or rolling feature |
| fact_weather | weather_id | Created by Postgres | Auto-numbered with `SERIAL` | Key: primary key |
| fact_weather | game_id | Matched in Python | Match the weather hour nearest the game's start time and link it to the Retrosheet `gid` | Key: links to `fact_game` |
| fact_weather | temp_c | Meteostat | Use `temp` from the hourly weather record nearest game start | Feature |
| fact_weather | precip_mm | Meteostat | Use `prcp` from the hourly weather record nearest game start | Feature |
| fact_weather | wind_speed_kmh | Meteostat | Use `wspd` from the hourly weather record nearest game start | Feature |

## Source fields used but not stored
- Retrosheet `hometeam`: used to identify Angels home games.
- Retrosheet `gametype`: used to identify regular-season games.
- Retrosheet `number`: used if needed to distinguish games played on the same date, such as a doubleheader.
- Statcast `game_pk`: used to group pitch records by game and match Statcast games to Retrosheet games.
- Statcast `game_date`: used to match games across sources.
- Statcast `home_team` and `away_team`: used to match games across sources.
- Statcast `game_year`: used to confirm the 2023–2025 scope.
- Statcast `game_type`: used to confirm regular-season games.
- Statcast `inning_topbot`: used to confirm Angels batting records for home games.
- Statcast `at_bat_number`: used to calculate plate appearances.
- Statcast `pitch_number`: used to identify pitch records.
- Meteostat `time`: converted to local game time and used to select the weather observation nearest the game's start time.