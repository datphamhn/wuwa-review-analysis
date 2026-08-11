# WuWa Steam Reviews - Sentiment Analysis & Review Classification

An end-to-end data science project analyzing Steam reviews for the gacha ARPG
*Wuthering Waves* (WuWa), collected directly from Steam's public API. The goal
is to understand how player sentiment has evolved since launch, identify what
drives negative reviews, and (in progress) build a classifier that predicts
whether a review will be Recommended or Not based on its features.

## Motivation

As a daily player of WuWa, I wanted to apply data analysis to a domain I
understand well enough to interpret correctly, using entirely self-collected
data rather than a pre-packaged dataset.

## Data Sources

Both pulled live from official, public, key-free Steam endpoints:

- **Reviews:** `store.steampowered.com/appreviews/{appid}` — Steam App Reviews API
- **Patch history:** `api.steampowered.com/ISteamNews/GetNewsForApp` — Steam News API
- AppID used: `3513350` (Wuthering Waves)

Collected dataset: **28,218 English-language reviews** (2025-04-28 to
2026-07-23) and **15 patch/news items**, later filtered to 14 actual patch
releases.

## Project Structure

```
wuwa-review-analysis/
├── data/                    # raw collected JSON (gitignored, not pushed)
├── notebooks/
│   └── 01_data_cleaning_eda.ipynb
├── src/
│   ├── collect_reviews.py   # paginated review collection via cursor
│   ├── collect_patches.py   # patch/news history collection
│   └── test_setup.py        # environment sanity check
├── requirements.txt
└── README.md
```

## Methodology

1. **Collection** — paginate through the Steam Reviews API (100 reviews/page,
   cursor-based) until exhausted; checkpoint every 20 pages to avoid data loss
   on interruption.
2. **Cleaning** — flatten nested JSON with `pd.json_normalize`, drop
   fields with 93%+ missingness (Steam Deck-only hardware info), drop
   reviewer-identifying fields (not needed for analysis, and avoided in
   the interest of not baking real usernames into a public notebook),
   normalize an inconsistently-typed field (`weighted_vote_score` comes
   back as either a string or a float depending on vote count), and
   validate with sanity checks (zero duplicate reviews, date range matches
   the game's actual Steam launch date).
3. **EDA** — weekly % positive over time, overlaid with patch release dates
   and review volume (to separate real signal from small-sample noise);
   deep dive into the lowest point in the sentiment timeline, testing and
   revising two hypotheses along the way using the review text and
   reviewer playtime rather than assumption.

## Key Findings

- Sentiment shows a **gradual decline**, not a single review-bomb event —
  from ~90% positive at launch to a noisier 80–85% band by mid-2026, with
  short-lived spikes around major content updates (most notably Version 3.0).
- The lowest point in the timeline (week of 2026-06-08) was initially
  suspected to be noise from a small sample, but at 865 reviews that week
  it turned out to be a real signal.
- That dip has a **mixed cause**: median playtime among reviewers that week
  was less than half the dataset-wide median, and ~17.5% of negative
  reviews mentioned onboarding friction (large download size, forced
  external account creation, a Discord Quest campaign driving new,
  low-intent installs) — but this is a contributing factor, not the
  dominant one. The remaining ~82.5% raised recurring, non-specific
  complaints (monetization, gacha fatigue) present across most weeks.

## Setup & Reproduction

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt

python src/collect_patches.py
python src/collect_reviews.py      # ~10-15 min, paginates ~28k reviews

# then open notebooks/01_data_cleaning_eda.ipynb and run all cells
```

## Limitations

- English-language reviews only (~62% of total reviews on this title),
  so non-English player sentiment isn't represented.
- Steam is only one of WuWa's platforms — a meaningful share of players use
  the game's own launcher rather than Steam, so this sample skews toward
  Steam-specific players.

## Status

- [x] Data collection
- [x] Cleaning & EDA
- [ ] Feature engineering
- [ ] Classification model (Recommended vs. Not) with class-imbalance handling
- [ ] Final write-up

## Tech Stack

Python, pandas, numpy, scikit-learn, matplotlib, seaborn, VADER (sentiment),
imbalanced-learn, Jupyter.

## Acknowledgments

I used Claude to help design the data pipeline, debug issues as they came up,
and review the analysis code throughout this project. I ran every step
myself, tested the results, and interpreted the findings using my own
understanding of Wuthering Waves as a player.
