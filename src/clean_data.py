
import os
import pandas as pd


RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "layoffs_raw.csv")
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "layoffs_clean.csv")


df = pd.read_csv(RAW_PATH)
print(f"Loaded {len(df)} rows from {RAW_PATH}\n")

df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=False, errors="coerce")
df["year"] = df["date"].dt.year.astype("Int64")    # nullable integer
df["month"] = df["date"].dt.month.astype("Int64")


df["location"] = (
    df["location"]
    .str.replace(r",\s*Non-U\.S\.\s*$", "", regex=True)
    .str.strip()
)


for col in ["industry", "stage", "country"]:
    df[col] = df[col].astype(str).str.strip().str.title()
    
    df.loc[df[col] == "Nan", col] = pd.NA

df["total_laid_off"] = pd.to_numeric(df["total_laid_off"], errors="coerce")
df["percentage_laid_off"] = pd.to_numeric(df["percentage_laid_off"], errors="coerce")
df["funds_raised"] = pd.to_numeric(df["funds_raised"], errors="coerce")
df.to_csv(CLEAN_PATH, index=False)
print(f"Saved cleaned data to {CLEAN_PATH}\n")

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
