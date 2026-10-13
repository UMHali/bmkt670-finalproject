# Field Sources
The prediction unit for this project is one Los Angeles Angels home game. The table below shows where every field in the database comes from and what it will be used for.

| Table | Field | Comes from | How | Used for |
|---|---|---|---|---|
| dim_team | team_id | Retrosheet + Statcast | Normalize Retrosheet `visteam` to the approved common Statcast-style opponent ID | Key: links each game to its opponent |
| dim_date | date_id | Retrosheet | Use `date` and convert it to a date type | Key: links each game to its date |
| dim_date | season | Retrosheet | Use `season` | Groups games by season and is used to create the time-based split |
| dim_date | day_of_week | Calculated in Python | pandas, from `date_id` | Feature |
| dim_date | month | Calculated in Python | pandas, from `date_id` | Feature |
| dim_date | is_weekend | Calculated in Python | Saturday or Sunday = True; otherwise False | Feature |
| fact_game | game_id | Retrosheet | Use `gid` | Key: one ID per game |
| fact_game | date_id | Retrosheet | Use `date` | Key: links to `dim_date` |
| fact_game | opponent_id | Retrosheet + Statcast | Normalize Retrosheet `visteam` to the approved common Statcast-style opponent ID | Key: links to `dim_team` |
| fact_game | start_time | Retrosheet | Use `starttime` | Input to `start_hour` and the weather match |
| fact_game | day_night | Retrosheet | Use `daynight` | Input to the encoded `is_night` feature |
| fact_game | home_runs | Retrosheet | Use `hruns` | Historical input to prior-game rolling features only |
| fact_game | away_runs | Retrosheet | Use `vruns` | Historical input to prior-game rolling features only |
| fact_game | duration_minutes | Retrosheet | Use `timeofgame` | Prediction target: duration_minutes |
| fact_game_metrics | metrics_id | Created by Postgres | Auto-numbered with `SERIAL` | Key: primary key |
| fact_game_metrics | game_id | Matched in Python | Match normalized date and opponent; use the four approved explicit doubleheader mappings; store Retrosheet `gid` | Key: links to `fact_game` |
| fact_game_metrics | angels_plate_appearances | Calculated in Python | Count unique `at_bat_number` values within each `game_pk` | Historical input to prior-game rolling features only |
| fact_weather | weather_id | Created by Postgres | Auto-numbered with `SERIAL` | Key: primary key |
| fact_weather | game_id | Matched in Python | Match the weather hour nearest the game's start time and link it to the Retrosheet `gid` | Key: links to `fact_game` |
| fact_weather | temp_c | Meteostat | Use `temp` from the hourly weather record nearest game start | Feature |
| fact_weather | precip_mm | Meteostat | Use `prcp` from the hourly weather record nearest game start | Feature |
| fact_weather | wind_speed_kmh | Meteostat | Use `wspd` from the hourly weather record nearest game start | Feature |

| ml_features_game_duration | game_id | Joined | Copy from `fact_game.game_id` | Key: identifies the game |
| ml_features_game_duration | date_id | Joined | Copy from `fact_game.date_id` | Key: identifies the game date |
| ml_features_game_duration | season | Joined | Copy from `dim_date.season` | Time-period field used to create the train, validate, and test split |
| ml_features_game_duration | opponent_id | Joined | Copy from `fact_game.opponent_id` | Opponent identifier; not used directly as a numeric model feature |
| ml_features_game_duration | month | Joined | Copy from `dim_date.month` | Feature |
| ml_features_game_duration | start_hour | Calculated in Python | Extract the hour from `start_time` | Feature |
| ml_features_game_duration | is_weekend | Joined | Copy from `dim_date.is_weekend` and store as 0/1 | Feature |
| ml_features_game_duration | is_night | Calculated in Python | Night = 1; day = 0 | Feature |
| ml_features_game_duration | dow_monday | Calculated in Python | Monday = 1; otherwise 0 | Encoded categorical feature |
| ml_features_game_duration | dow_tuesday | Calculated in Python | Tuesday = 1; otherwise 0 | Encoded categorical feature |
| ml_features_game_duration | dow_wednesday | Calculated in Python | Wednesday = 1; otherwise 0 | Encoded categorical feature |
| ml_features_game_duration | dow_thursday | Calculated in Python | Thursday = 1; otherwise 0 | Encoded categorical feature |
| ml_features_game_duration | dow_friday | Calculated in Python | Friday = 1; otherwise 0 | Encoded categorical feature |
| ml_features_game_duration | dow_saturday | Calculated in Python | Saturday = 1; otherwise 0 | Encoded categorical feature |
| ml_features_game_duration | dow_sunday | Calculated in Python | Sunday = 1; otherwise 0 | Encoded categorical feature |
| ml_features_game_duration | temp_c | Joined | Copy from `fact_weather.temp_c` | Feature |
| ml_features_game_duration | precip_mm | Joined | Copy from `fact_weather.precip_mm` | Feature |
| ml_features_game_duration | wind_speed_kmh | Joined | Copy from `fact_weather.wind_speed_kmh` | Feature |
| ml_features_game_duration | rolling_avg_duration_prev5 | Calculated in Python | Use `shift(1)` and the previous five home-game durations | Derived feature using only prior games |
| ml_features_game_duration | rolling_avg_total_runs_prev5 | Calculated in Python | Calculate total runs, then use `shift(1)` and the previous five home games | Derived feature using only prior games |
| ml_features_game_duration | rolling_avg_plate_appearances_prev5 | Calculated in Python | Use `shift(1)` and the previous five Angels home-game plate-appearance totals | Derived feature using only prior games |
| ml_features_game_duration | days_since_last_home_game | Calculated in Python | Difference between the current game date and previous home-game date | Derived feature |
| ml_features_game_duration | duration_minutes | Joined | Copy from `fact_game.duration_minutes` | Prediction target |
| ml_features_game_duration | split | Calculated in Python | 2023 = train; 2024 = validate; 2025 = test | Time-based model split |

## Source fields used but not stored
- Retrosheet `hometeam`: used to identify Angels home games.
- Retrosheet `gametype`: used to identify regular-season games.
- Retrosheet `number`: used during review of the 2023 doubleheader records.
- Statcast `game_pk`: used to group pitch records by game and match Statcast games to Retrosheet games.
- Statcast `game_date`: used to match games across sources.
- Statcast `home_team` and `away_team`: used to match games across sources.
- Statcast `game_year`: used to confirm the 2023–2025 scope.
- Statcast `game_type`: used to confirm regular-season games.
- Statcast `inning_topbot`: used to confirm Angels batting records for home games.
- Statcast `at_bat_number`: used to calculate plate appearances.
- Statcast `pitch_number`: used during source validation to check for duplicate or incomplete pitch sequences.
- Meteostat `time`: converted to local game time and used to select the weather observation nearest the game's start time.

## Approved doubleheader mapping
Historical recorded scores verified these identifiers. Scores are used only for source matching, never as current-game predictors.

| Statcast game_pk (used but not stored) | Retrosheet gid | Game date | Game number |
| --- | --- | --- | --- |
| 716915 | ANA202308191 | 2023-08-19 | 1 |
| 716925 | ANA202308192 | 2023-08-19 | 2 |
| 716890 | ANA202308231 | 2023-08-23 | 1 |
| 716903 | ANA202308232 | 2023-08-23 | 2 |

## Approved opponent normalization
Retrosheet to common Statcast IDs: ARI→AZ, CHA→CWS, CHN→CHC, KCA→KC, LAN→LAD, NYA→NYY, NYN→NYM, SDN→SD, SFN→SF, SLN→STL, TBA→TB, WAS→WSH, OAK→ATH, ATH→ATH. Other codes are retained only when they exactly match a Statcast opponent code. No full-team-name lookup is used.

Only the three annual Statcast files are used. Automatic-ball and automatic-strike records are retained for plate-appearance identification; no delivered-pitch count is calculated. Historical results are shifted before rolling and ordered by date plus start time. No pre-2023 games enter history. Weather is historical observed weather; live pregame use requires available forecast inputs. Retrosheet starttime is the requested source, and should be reviewed before treating it as a scheduled pregame value.