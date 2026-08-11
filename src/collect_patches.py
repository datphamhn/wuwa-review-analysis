"""
Fetch Wuthering Waves' patch/update history from the Steam News API
and save it to data/patches_raw.json.
Used later to overlay against the review sentiment timeline.

Run: python src/collect_patches.py
"""

import requests
import json
import os

APP_ID = 3513350
OUTPUT_PATH = "data/patches_raw.json"
URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)

    params = {
        "appid": APP_ID,
        "count": 1000,  
        "maxlength": 0,  
        "format": "json",
    }
    r = requests.get(URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    items = data.get("appnews", {}).get("newsitems", [])
    print(f"Fetched {len(items)} news/patch items.")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)

    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()