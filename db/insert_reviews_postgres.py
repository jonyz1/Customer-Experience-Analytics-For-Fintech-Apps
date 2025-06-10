import pandas as pd
import psycopg2
from tqdm import tqdm
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load your sentiment-enhanced CSV
df = pd.read_csv("data/sentiment_reviews.csv")

# Get database connection details from environment variables
db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Connect to PostgreSQL
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS banks (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY,
        review TEXT NOT NULL,
        rating INT NOT NULL,
        date DATE NOT NULL,
        bank_id INT REFERENCES banks(id),
        source TEXT,
        sentiment_label TEXT,
        sentiment_score FLOAT
    );
""")
conn.commit()

# Fetch existing bank name → id mapping
cursor.execute("SELECT name, id FROM banks;")
bank_id_map = dict(cursor.fetchall())

# Insert data
for _, row in tqdm(df.iterrows(), total=len(df)):
    bank_name = row['bank']

    # Insert bank if new
    if bank_name not in bank_id_map:
        cursor.execute("INSERT INTO banks (name) VALUES (%s) RETURNING id;", (bank_name,))
        bank_id = cursor.fetchone()[0]
        bank_id_map[bank_name] = bank_id
    else:
        bank_id = bank_id_map[bank_name]

    cursor.execute("""
        INSERT INTO reviews (
            review, rating, date, bank_id, source, sentiment_label, sentiment_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (
        row['review'],
        int(row['rating']),
        row['date'],
        bank_id,
        row.get('source', 'unknown'),  
        row['sentiment_label'],
        float(row['sentiment_score'])
    ))

# Finalize
conn.commit()
cursor.close()
conn.close()
