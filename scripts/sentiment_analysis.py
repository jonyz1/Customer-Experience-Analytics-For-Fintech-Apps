import pandas as pd
from transformers import pipeline
from tqdm import tqdm
import os


# Load cleaned CSVs
CLEAN_DATA_DIR = "data/clean"
all_files = pd.concat([pd.read_csv(f"{CLEAN_DATA_DIR}/{f}") for f in os.listdir(CLEAN_DATA_DIR) if f.endswith(".csv")])

# Initialize sentiment pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Run sentiment analysis
def classify_sentiment(text):
    try:
        result = sentiment_pipeline(text[:512])[0]  # Limit to 512 tokens
        label = result['label'].lower()
        score = result['score']
        return label, score
    except:
        return "error", 0.0

# Apply to data
tqdm.pandas()
all_files[['sentiment_label', 'sentiment_score']] = all_files['review'].progress_apply(
    lambda x: pd.Series(classify_sentiment(str(x)))
)

# Save results
all_files.to_csv("data/sentiment_reviews.csv", index=False)

# Aggregate sentiment by bank and rating
summary = all_files.groupby(['bank', 'rating', 'sentiment_label']).agg(
    count=('sentiment_label', 'count'),
    avg_score=('sentiment_score', 'mean')
).reset_index()

summary.to_csv("data/sentiment_summary.csv", index=False)
print(summary.head())
