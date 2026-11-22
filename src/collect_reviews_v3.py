"""
Collect Wuthering Waves Steam reviews (v3, GetAppReviews API).

Why v3: Valve retired the old store.steampowered.com/appreviews endpoint on
2026-10-22 (it now redirects to the Steam homepage). v3 uses the replacement
Web API: api.steampowered.com/IUserReviewsService/GetAppReviews/v1/ (no key).

Also new in v3:
- Retries a failed page (waits 10s, 20s, 40s...) instead of crashing.
- Saves the cursor with every checkpoint, so re-running resumes where it stopped.
- Optional date range (DATE_START / DATE_END) to re-collect a fixed period.

Run from the repo root:  python src/collect_reviews_v3.py
"""

import requests
import json
import time
import os
from datetime import datetime, timezone

APP_ID = 3513350
OUTPUT_PATH = "data/reviews_raw.json"
STATE_PATH = "data/reviews_checkpoint_state.json"
URL = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/"
MAX_RETRIES = 6

# Leave both as None to collect everything up to today.
# To match the original dataset, use e.g. "2025-04-28" and "2026-07-23".
DATE_START = None
DATE_END = None


def to_unix(d, end_of_day=False):
    t = datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if end_of_day:
        t = t.replace(hour=23, minute=59, second=59)
    return int(t.timestamp())


def fetch_page(cursor="*"):
    query = {
        "appid": APP_ID,
        "filter": 1,            # 1 = recent (newest first)
        "review_type": 0,       # 0 = all
        "purchase_type": 1,     # 1 = all
        "languages": ["english"],
        "num_per_page": 100,
        "cursor": cursor,
    }
    if DATE_START and DATE_END:
        query["date_range_start"] = to_unix(DATE_START)
        query["date_range_end"] = to_unix(DATE_END, end_of_day=True)

    wait = 10
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(URL, params={"input_json": json.dumps(query)},
                             headers={"User-Agent": "wuwa-review-analysis/1.0"},
                             timeout=30)
            r.raise_for_status()
            return r.json().get("response", {})
        except (requests.RequestException, ValueError) as e:
            print(f"  ! attempt {attempt}/{MAX_RETRIES} failed ({type(e).__name__}: {e}), waiting {wait}s...")
            time.sleep(wait)
            wait *= 2
    raise RuntimeError("Steam kept failing on this page. Run the script again later to resume.")


def save(all_reviews, cursor, page):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"cursor": cursor, "page": page}, f)


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)

    all_reviews, cursor, page = [], "*", 0
    if os.path.exists(STATE_PATH) and os.path.exists(OUTPUT_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            state = json.load(f)
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            all_reviews = json.load(f)
        cursor, page = state["cursor"], state["page"]
        print(f"Resuming from checkpoint: page {page}, {len(all_reviews)} reviews")

    seen = {r["recommendationid"] for r in all_reviews}

    while True:
        data = fetch_page(cursor)
        batch = data.get("reviews", [])

        if page == 0 and not batch:
            print("First page returned no reviews. Raw response (first 500 chars):")
            print(json.dumps(data)[:500])
            break
        if not batch:
            print("No more reviews to fetch, stopping.")
            break

        new = [r for r in batch if r["recommendationid"] not in seen]
        all_reviews.extend(new)
        seen.update(r["recommendationid"] for r in new)
        page += 1
        print(f"Page {page}: +{len(new)} reviews | Total so far: {len(all_reviews)}")

        new_cursor = data.get("cursor")
        if not new_cursor or new_cursor == cursor:
            print("Cursor stopped changing, all reviews collected.")
            break
        cursor = new_cursor

        if page % 20 == 0:
            save(all_reviews, cursor, page)
            print(f"  -> checkpoint saved: {len(all_reviews)} reviews")

        time.sleep(1)

    save(all_reviews, cursor, page)
    if os.path.exists(STATE_PATH):
        os.remove(STATE_PATH)
    print(f"\nDONE. Total reviews collected: {len(all_reviews)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
