# Missing Data
| Table / Source | Column | % missing | Decision | Why |
|---|---|---:|---|---|
| fact_game_metrics clean CSV | metrics_id | 100.00% | Leave blank in the clean CSV | PostgreSQL creates this value with `SERIAL` during loading |
| fact_weather clean CSV | weather_id | 100.00% | Leave blank in the clean CSV | PostgreSQL creates this value with `SERIAL` during loading |
| ML before first-row removal | rolling_avg_duration_prev5 | 0.41% | Remove the first ML row only | The first 2023 home game has no earlier post-pitch-clock home-game history |
| ML before first-row removal | rolling_avg_total_runs_prev5 | 0.41% | Remove the first ML row only | The first 2023 home game has no earlier post-pitch-clock home-game history |
| ML before first-row removal | rolling_avg_plate_appearances_prev5 | 0.41% | Remove the first ML row only | The first 2023 home game has no earlier post-pitch-clock home-game history |
| ML before first-row removal | days_since_last_home_game | 0.41% | Remove the first ML row only | The first 2023 home game has no earlier post-pitch-clock home-game history |
| Raw Meteostat data | prcp | 0.08% (20 of 26,304 rows) | Leave unchanged | None of the missing precipitation rows are selected for one of the 243 game-level weather matches |

Before the ML row is removed, each historical rolling field and `days_since_last_home_game` has 1 missing value out of 243 rows. All four missing values occur on `ANA202304070`, the first Angels home game in the project period.

That game is removed only from `ml_features_game_duration`. It remains in the historical fact tables. Pre-2023 data are not used because the project begins with the 2023 pitch-clock environment.

The rolling averages use `shift(1)` before `rolling(5, min_periods=1)`. This means the current game is never included in its own feature. Games two through five use the prior history that is available, and later games use the previous five home games.

All 242 final ML rows have no missing values. No blanket `dropna()` or general imputation is used.

The raw weather files contain 20 missing precipitation observations, but none is used for one of the 243 matched game-weather rows. Those raw values remain unchanged. No selected weather timestamp is duplicated, and every selected weather hour is within 30 minutes of game start.