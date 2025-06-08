import csv
import glob
import os
import logging
from datetime import datetime

# Setup Logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load all raw CSV files
def load_raw_reviews():
    all_reviews = []
    raw_files = glob.glob('data/raw/*.csv')
    logging.info(f"Found {len(raw_files)} raw CSV files to process.")

    for file in raw_files:
        logging.info(f"Processing {file}...")
        with open(file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['review'].strip():  # Skip empty reviews
                    all_reviews.append(row)

    logging.info(f"Loaded {len(all_reviews)} raw reviews.")
    return all_reviews

# Preprocessing: remove duplicates
def remove_duplicates(reviews_list):
    unique_reviews = { (r['review'], r['rating'], r['date'], r['bank']): r for r in reviews_list }
    cleaned_reviews = list(unique_reviews.values())
    logging.info(f"Reduced to {len(cleaned_reviews)} unique reviews after removing duplicates.")
    return cleaned_reviews

# Save cleaned reviews per bank
def save_clean_reviews_per_bank(cleaned_reviews):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('data/clean', exist_ok=True)

    # Group by bank
    bank_groups = {}
    for review in cleaned_reviews:
        bank = review['bank']
        if bank not in bank_groups:
            bank_groups[bank] = []
        bank_groups[bank].append(review)

    # Save each bank to separate CSV
    for bank, reviews in bank_groups.items():
        filename = f"data/clean/{bank.replace(' ', '_')}_cleaned_reviews_{timestamp}.csv"
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['review', 'rating', 'date', 'bank', 'source'])
            writer.writeheader()
            for review in reviews:
                writer.writerow(review)

        logging.info(f"Saved {len(reviews)} cleaned reviews to {filename}")

# Main
def main():
    raw_reviews = load_raw_reviews()
    cleaned_reviews = remove_duplicates(raw_reviews)
    save_clean_reviews_per_bank(cleaned_reviews)

if __name__ == '__main__':
    main()
