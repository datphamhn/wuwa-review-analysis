import requests
import json
import time
import os

APP_ID = 3513350  
OUTPUT_PATH = "data/reviews_raw.json"
BASE_URL = f"https://store.steampowered.com/appreviews/{APP_ID}"


def fetch_page(cursor="*"):
    params = {
        "json": 1,
        "filter": "recent",   
        "language": "english", 
        "num_per_page": 100,    
        "purchase_type": "all",
        "cursor": cursor,
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)

    all_reviews = []
    cursor = "*"
    page = 0

    while True:
        data = fetch_page(cursor)
        if data.get("success") != 1:
            print("Steam API returned an error, stopping.")
            break

        reviews = data.get("reviews", [])
        if not reviews:
            print("No more reviews to fetch, stopping.")
            break

        all_reviews.extend(reviews)
        page += 1
        print(f"Page {page}: +{len(reviews)} reviews | Total so far: {len(all_reviews)}")

        new_cursor = data.get("cursor")
        if new_cursor == cursor:
            print("Cursor stopped changing, all reviews collected.")
            break
        cursor = new_cursor

        if page % 20 == 0:
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(all_reviews, f, ensure_ascii=False)
            print(f"  -> checkpoint saved: {len(all_reviews)} reviews to {OUTPUT_PATH}")

        time.sleep(1)  # be polite to the server, avoid getting rate-limited

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False)

    print(f"\nDONE. Total reviews collected: {len(all_reviews)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()