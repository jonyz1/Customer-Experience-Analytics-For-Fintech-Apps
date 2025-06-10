import os
import pandas as pd
import spacy
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer


# Load English NLP model
nlp = spacy.load("en_core_web_sm")

# Load data
df = pd.read_csv("data/sentiment_reviews.csv") 
tqdm.pandas()

# Clean & lemmatize text
def preprocess(text):
    doc = nlp(str(text))
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and token.is_alpha]
    return " ".join(tokens)

df["clean_review"] = df["review"].progress_apply(preprocess)

# Extract top keywords
def extract_keywords(texts, top_n=10):
    vectorizer = TfidfVectorizer(max_df=0.9, min_df=2, ngram_range=(1,2))
    tfidf_matrix = vectorizer.fit_transform(texts)
    scores = zip(vectorizer.get_feature_names_out(), tfidf_matrix.sum(axis=0).tolist()[0])
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return sorted_scores[:top_n]

# Get top keywords per bank
bank_keywords = {}
for bank in df['bank'].unique():
    bank_df = df[df['bank'] == bank]
    keywords = extract_keywords(bank_df['clean_review'])
    bank_keywords[bank] = keywords

# View top keywords
for bank, keywords in bank_keywords.items():
    print(f"\n{bank}")
    for word, score in keywords:
        print(f"{word}: {round(score, 2)}")

# Sample rule-based keyword → theme mapping
theme_map = {
    "login": "Account Access Issues",
    "password": "Account Access Issues",
    "slow": "Performance",
    "transfer": "Transaction Issues",
    "crash": "App Reliability",
    "support": "Customer Support",
    "agent": "Customer Support",
    "interface": "User Experience",
    "design": "User Experience",
    "feature": "Feature Requests"
}

# Match themes per review
def identify_themes(text):
    themes = set()
    for word in text.split():
        for keyword, theme in theme_map.items():
            if keyword in word:
                themes.add(theme)
    return list(themes) if themes else ["Miscellaneous"]

df['identified_themes'] = df['clean_review'].apply(identify_themes)

df.to_csv("data/thematic_reviews.csv", index=False)
