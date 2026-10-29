# --------------------------------------
# File: train_model.py
# Author: Hali Evans
# Purpose: Read the ML feature table from Postgres and explore the training data.
# Created: October 29, 2026
# --------------------------------------

import os
import warnings

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

load_dotenv()

warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy"
)

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

df = pd.read_sql(
    "SELECT * FROM ml_features_game_duration;",
    connection
)

connection.close()

train = df[df["split"] == "train"]
validate = df[df["split"] == "validate"]
test = df[df["split"] == "test"]

print(f"All ML rows: {len(df)}")
print(f"Train rows: {len(train)}")
print(f"Validate rows: {len(validate)}")
print(f"Test rows: {len(test)}")

if len(train) == 0 or len(validate) == 0 or len(test) == 0:
    raise ValueError("One or more split DataFrames are empty")

fig1, ax = plt.subplots()

plt.hist(train["duration_minutes"])
plt.xlabel("Game duration (minutes)")
plt.ylabel("Frequency")

fig1.savefig(
    "docs/figures/duration_histogram.png"
)

fig2, ax = plt.subplots()

plt.scatter(
    train["rolling_avg_duration_prev5"],
    train["duration_minutes"]
)
plt.xlabel("Previous 5-game average duration")
plt.ylabel("Game duration (minutes)")

fig2.savefig(
    "docs/figures/duration_vs_previous_duration.png"
)

fig3, ax = plt.subplots()

plt.scatter(
    train["rolling_avg_plate_appearances_prev5"],
    train["duration_minutes"]
)
plt.xlabel("Previous 5-game average plate appearances")
plt.ylabel("Game duration (minutes)")

fig3.savefig(
    "docs/figures/duration_vs_plate_appearances.png"
)

print("Saved charts to docs/figures.")

baseline_guess = train["duration_minutes"].mean()

baseline_mae = mean_absolute_error(
    validate["duration_minutes"],
    [baseline_guess] * len(validate)
)

print(f"Baseline guess: {baseline_guess:.2f} minutes")
print(f"Baseline MAE: {baseline_mae:.2f} minutes")

feature_columns = [
    "month",
    "start_hour",
    "is_weekend",
    "is_night",
    "temp_c",
    "precip_mm",
    "wind_speed_kmh",
    "rolling_avg_duration_prev5",
    "rolling_avg_total_runs_prev5",
    "rolling_avg_plate_appearances_prev5",
    "days_since_last_home_game"
]

X_train = train[feature_columns].values
X_validate = validate[feature_columns].values
X_test = test[feature_columns].values

y_train = train["duration_minutes"].values
y_validate = validate["duration_minutes"].values
y_test = test["duration_minutes"].values

linear_regression = LinearRegression().fit(
    X_train,
    y_train
)

linear_predictions = linear_regression.predict(
    X_validate
)

linear_mae = mean_absolute_error(
    y_validate,
    linear_predictions
)

print(
    f"Linear Regression Validate MAE: "
    f"{linear_mae:.2f} minutes"
)

standard_scaler = StandardScaler()

standard_scaler.fit(X_train)

X_train_scaled = standard_scaler.transform(
    X_train
)

X_validate_scaled = standard_scaler.transform(
    X_validate
)

X_test_scaled = standard_scaler.transform(
    X_test
)

knn = KNeighborsRegressor(
    n_neighbors=5,
    p=2,
    metric="minkowski",
    weights="uniform",
    algorithm="auto"
)

knn.fit(
    X_train_scaled,
    y_train
)

knn_predictions = knn.predict(
    X_validate_scaled
)

knn_mae = mean_absolute_error(
    y_validate,
    knn_predictions
)

print(
    f"KNN Regression Validate MAE: "
    f"{knn_mae:.2f} minutes"
)

decision_tree = DecisionTreeRegressor(
    random_state=42
)

decision_tree.fit(
    X_train,
    y_train
)

tree_predictions = decision_tree.predict(
    X_validate
)

tree_mae = mean_absolute_error(
    y_validate,
    tree_predictions
)

print(
    f"Decision Tree Validate MAE: "
    f"{tree_mae:.2f} minutes"
)

model_results = pd.DataFrame(
    {
        "Model": [
            "Baseline",
            "Linear Regression",
            "KNN Regression",
            "Decision Tree"
        ],
        "Validate MAE": [
            baseline_mae,
            linear_mae,
            knn_mae,
            tree_mae
        ]
    }
)

print("\nModel comparison:")
print(model_results)

knn_test_predictions = knn.predict(
    X_test_scaled
)

knn_train_predictions = knn.predict(
    X_train_scaled
)

knn_test_mae = mean_absolute_error(
    y_test,
    knn_test_predictions
)

print(
    f"\nKNN Regression Test MAE: "
    f"{knn_test_mae:.2f} minutes"
)

importance_regression = LinearRegression().fit(
    X_train_scaled,
    y_train
)

coefficient_table = pd.DataFrame(
    {
        "Feature": feature_columns,
        "Coefficient": importance_regression.coef_
    }
)

print("\nLinear Regression coefficients:")
print(coefficient_table)

train_predictions = pd.DataFrame(
    {
        "game_id": train["game_id"].values,
        "split": train["split"].values,
        "actual": y_train,
        "predicted": knn_train_predictions
    }
)

validate_predictions = pd.DataFrame(
    {
        "game_id": validate["game_id"].values,
        "split": validate["split"].values,
        "actual": y_validate,
        "predicted": knn_predictions
    }
)

test_predictions = pd.DataFrame(
    {
        "game_id": test["game_id"].values,
        "split": test["split"].values,
        "actual": y_test,
        "predicted": knn_test_predictions
    }
)

predictions = pd.concat(
    [
        train_predictions,
        validate_predictions,
        test_predictions
    ]
)

predictions["error"] = (
    predictions["actual"] - predictions["predicted"]
)

predictions["model_name"] = "KNN Regression"

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = connection.cursor()

cursor.execute(
    "DELETE FROM model_predictions;"
)

for _, row in predictions.iterrows():
    cursor.execute(
        """
        INSERT INTO model_predictions (
            game_id,
            split,
            actual,
            predicted,
            error,
            model_name
        )
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        (
            row["game_id"],
            row["split"],
            float(row["actual"]),
            float(row["predicted"]),
            float(row["error"]),
            row["model_name"]
        )
    )

connection.commit()

cursor.close()
connection.close()

print(
    f"\nSaved {len(predictions)} predictions "
    "to model_predictions."
)