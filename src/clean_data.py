"""
clean_data.py — Cleans the raw layoffs CSV and saves a standardized version.

Steps:
  1. Parse the 'date' column to datetime; extract year and month
  2. Strip ", Non-U.S." suffix from locations for consistency
  3. Title-case and trim industry, stage, country
  4. Coerce numeric columns (total_laid_off, percentage_laid_off, funds_raised) to float
  5. Keep ALL rows (even those missing total_laid_off)
  6. Save to data/layoffs_clean.csv
  7. Print a summary of the cleaned dataset
"""

import os
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────
RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "layoffs_raw.csv")
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "layoffs_clean.csv")

# ── Load ─────────────────────────────────────────────────────────────────
df = pd.read_csv(RAW_PATH)
print(f"Loaded {len(df)} rows from {RAW_PATH}\n")

# ── 1. Date parsing ─────────────────────────────────────────────────────
# Parse 'date' column (format like 6/17/2026) into datetime
df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=False, errors="coerce")
df["year"] = df["date"].dt.year.astype("Int64")    # nullable integer
df["month"] = df["date"].dt.month.astype("Int64")

# ── 2. Clean location — strip ", Non-U.S." and similar suffixes ─────────
df["location"] = (
    df["location"]
    .str.replace(r",\s*Non-U\.S\.\s*$", "", regex=True)
    .str.strip()
)

# ── 3. Standardize text columns to title case, trimmed ───────────────────
for col in ["industry", "stage", "country"]:
    df[col] = df[col].astype(str).str.strip().str.title()
    # Title-casing converts "nan" → "Nan"; fix that back to real NaN
    df.loc[df[col] == "Nan", col] = pd.NA

# ── 4. Coerce numeric columns ───────────────────────────────────────────
df["total_laid_off"] = pd.to_numeric(df["total_laid_off"], errors="coerce")
df["percentage_laid_off"] = pd.to_numeric(df["percentage_laid_off"], errors="coerce")
df["funds_raised"] = pd.to_numeric(df["funds_raised"], errors="coerce")

# ── 5. Save ──────────────────────────────────────────────────────────────
df.to_csv(CLEAN_PATH, index=False)
print(f"Saved cleaned data to {CLEAN_PATH}\n")

# ── 6. Summary ───────────────────────────────────────────────────────────
total_rows = len(df)
missing_laid_off = df["total_laid_off"].isna().sum()
date_min = df["date"].min().strftime("%Y-%m-%d") if df["date"].notna().any() else "N/A"
date_max = df["date"].max().strftime("%Y-%m-%d") if df["date"].notna().any() else "N/A"
unique_countries = df["country"].dropna().nunique()
unique_industries = df["industry"].dropna().nunique()

print("=" * 50)
print("  CLEANED DATA SUMMARY")
print("=" * 50)
print(f"  Total rows:              {total_rows}")
print(f"  Missing total_laid_off:  {missing_laid_off}")
print(f"  Date range:              {date_min}  ->  {date_max}")
print(f"  Unique countries:        {unique_countries}")
print(f"  Unique industries:       {unique_industries}")
print("=" * 50)
