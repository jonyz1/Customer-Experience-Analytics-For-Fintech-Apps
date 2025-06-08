from google_play_scraper import Sort, reviews
import csv
from datetime import datetime
import logging
import os

# Setup Logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Apps to scrape
apps = [
    {'app_id': 'com.combanketh.mobilebanking', 'bank_name': 'Commercial Bank of Ethiopia'},
    {'app_id': 'com.boa.boaMobileBanking', 'bank_name': 'Bank of Abyssinia'},
    {'app_id': 'com.dashen.dashensuperapp', 'bank_name': 'Dashen Bank'}
]

# Scraping function
def scrape_reviews_for_bank(app_id, bank_name):
    logging.info(f"Fetching reviews for {bank_name}...")
    try:
        results, _ = reviews(
            app_id,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=400,  
            filter_score_with=None
        )
        logging.info(f"✅Fetched {len(results)} reviews for {bank_name}.")
        return [
            {
                'review': entry['content'],
                'rating': entry['score'],
                'date': entry['at'].strftime('%Y-%m-%d'),
                'bank': bank_name,
                'source': 'Google Play'
            }
            for entry in results
        ]
    except Exception as e:
        logging.error(f"Error occurred for {bank_name}: {e}")
        return []

# Save to CSV
def save_reviews_to_csv(reviews_list, bank_name):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('data/raw', exist_ok=True)
    filename = f'data/raw/{bank_name.replace(" ", "_")}_reviews_raw_{timestamp}.csv'

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['review', 'rating', 'date', 'bank', 'source'])
        writer.writeheader()
        for review in reviews_list:
            writer.writerow(review)

    logging.info(f"Saved raw reviews to {filename}")

# Main
def main():
    for app in apps:
        bank_reviews = scrape_reviews_for_bank(app['app_id'], app['bank_name'])
        save_reviews_to_csv(bank_reviews, app['bank_name'])

if __name__ == '__main__':
    main()
