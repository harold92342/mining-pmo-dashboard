"""
Build data/source/flotation_daily_2017.csv from the public Kaggle dataset
"Quality Prediction in a Mining Process" (Eduardo Magalhães Oliveira, CC0 Public Domain).

1. Download MiningProcess_Flotation_Plant_Database.csv from Kaggle
   (https://www.kaggle.com/datasets/edumagalhaes/quality-prediction-in-a-mining-process)
   and place it in data/source/.
2. Run:  python scripts/prepare_kaggle.py

The raw file holds readings every 20 seconds, stamped to the hour, with comma
decimals. This script averages them per hour, then per day, and keeps
11 Mar – 9 Sep 2017 (171 days). generate_data.py later shifts the dates by nine years (2017 -> 2026).
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "source" / "MiningProcess_Flotation_Plant_Database.csv"
OUT = ROOT / "data" / "source" / "flotation_daily_2017.csv"

raw = pd.read_csv(RAW, decimal=",", parse_dates=["date"])

hourly = raw.groupby("date").mean(numeric_only=True)
daily = hourly.groupby(hourly.index.normalize()).mean().round(4)
daily = daily.loc["2017-03-11":"2017-09-09"]   # the 171 full days used in the report
daily.index.name = "date"

daily.reset_index().to_csv(OUT, index=False, date_format="%Y-%m-%d")
print(f"{len(daily)} days written to {OUT.relative_to(ROOT)}")
