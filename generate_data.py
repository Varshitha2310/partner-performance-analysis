"""Generates a SIMULATED partner (publisher) performance dataset.
Run: python generate_data.py
Output: data/partner_performance.csv
NOTE: This data is synthetic and created for learning/portfolio purposes.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# partner name, type, base CPC (cost per click), apply rate, hire rate
partners = [
    ("JobHub Global", "Job Board", 0.45, 0.080, 0.050),
    ("CareerBridge", "Job Board", 0.55, 0.065, 0.040),
    ("WorkNest", "Job Board", 0.60, 0.050, 0.030),
    ("TalentStream", "Aggregator", 0.30, 0.040, 0.020),
    ("ApplyFast", "Aggregator", 0.28, 0.035, 0.015),
    ("JobScout", "Aggregator", 0.35, 0.045, 0.025),
    ("TechHire Network", "Niche Board", 0.90, 0.110, 0.080),
    ("HealthJobs Pro", "Niche Board", 0.85, 0.100, 0.070),
    ("LogisticsCareers", "Niche Board", 0.70, 0.090, 0.060),
    ("SocialReach Ads", "Social", 0.40, 0.030, 0.010),
    ("PeopleFeed", "Social", 0.38, 0.028, 0.012),
    ("CampusConnect", "Campus Portal", 0.50, 0.095, 0.045),
    ("RegionalJobs IN", "Regional Board", 0.25, 0.070, 0.035),
    ("EuroWork", "Regional Board", 0.65, 0.060, 0.030),
    ("GulfCareers", "Regional Board", 0.75, 0.055, 0.028),
]
regions = ["North America", "Europe", "Asia-Pacific"]
months = pd.period_range("2026-01", "2026-06", freq="M").astype(str)

rows = []
for month in months:
    for name, ptype, cpc, apply_rate, hire_rate in partners:
        for region in regions:
            clicks = int(rng.integers(800, 6000))
            c = max(0.1, rng.normal(cpc, cpc * 0.10))
            spend = round(clicks * c, 2)
            applies = int(clicks * max(0.005, rng.normal(apply_rate, apply_rate * 0.15)))
            hires = int(applies * max(0.0, rng.normal(hire_rate, hire_rate * 0.25)))
            rows.append([month, name, ptype, region, spend, clicks, applies, hires])

df = pd.DataFrame(rows, columns=["month", "partner", "partner_type", "region",
                                 "spend_usd", "clicks", "applies", "hires"])
df.to_csv("data/partner_performance.csv", index=False)
print(f"Saved {len(df)} rows to data/partner_performance.csv")
