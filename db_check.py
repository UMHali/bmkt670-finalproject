import os

import psycopg2
from dotenv import load_dotenv

# Load the database information from .env.
load_dotenv()

# Connect to the PostgreSQL database.
connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# Create a cursor so Python can run a SQL query.
cursor = connection.cursor()

# Find all tables in the public schema.
cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")

tables = cursor.fetchall()

# Print the table names.
print("Tables in the public schema:")

for table in tables:
    print(table[0])

# Close the database connection.
cursor.close()
connection.close()