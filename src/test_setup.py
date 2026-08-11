import requests
import pandas as pd
import numpy as np
import sklearn
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

print("Python OK:", pd.__version__, "| numpy:", np.__version__, "| sklearn:", sklearn.__version__)

APP_ID = 3513350

try:
    r = requests.get(
        f"https://store.steampowered.com/appreviews/{APP_ID}",
        params={"json": 1, "filter": "all", "language": "english", "num_per_page": 5, "cursor": "*"},
        timeout=5,
    )
    if r.status_code == 200 and r.json().get("success") == 1:
        n = len(r.json()["reviews"])
        print(f"Steam API connection: OK, fetched {n} sample reviews from WuWa")
    else:
        print("Steam API returned an error, status:", r.status_code)
except Exception as e:
    print("Steam API connection error:", e)

analyzer = SentimentIntensityAnalyzer()
print("Sentiment test:", analyzer.polarity_scores("This game is great!"))

print("Setup COMPLETE")