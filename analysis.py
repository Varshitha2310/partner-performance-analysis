"""Partner & channel performance analysis.
Run: python generate_data.py && python analysis.py
Outputs: charts/*.png, data/partner_summary.csv, console insights
"""
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/partner_performance.csv")

# ---------- 1. KPIs ----------
def add_kpis(d):
    d = d.copy()
    d["cpc"] = d["spend_usd"] / d["clicks"]
    d["apply_rate"] = d["applies"] / d["clicks"]
    d["cost_per_apply"] = d["spend_usd"] / d["applies"]
    d["cost_per_hire"] = d["spend_usd"] / d["hires"].replace(0, pd.NA)
    return d

# ---------- 2. Partner-level summary ----------
agg = df.groupby(["partner", "partner_type"], as_index=False)[
    ["spend_usd", "clicks", "applies", "hires"]].sum()
summary = add_kpis(agg)

# ---------- 3. Segment partners ----------
med_cpa = summary["cost_per_apply"].median()
med_apply_rate = summary["apply_rate"].median()

def segment(r):
    if r["cost_per_apply"] <= med_cpa and r["apply_rate"] >= med_apply_rate:
        return "Scale"      # efficient and good quality traffic
    if r["cost_per_apply"] > med_cpa and r["apply_rate"] < med_apply_rate:
        return "Review/Pause"  # expensive and low quality
    return "Optimize"       # mixed signals

summary["recommendation"] = summary.apply(segment, axis=1)
summary = summary.sort_values("cost_per_apply").round(3)
summary.to_csv("data/partner_summary.csv", index=False)

# ---------- 4. Insights ----------
total_spend = summary["spend_usd"].sum()
print("=" * 60)
print(f"Total spend: ${total_spend:,.0f} | Applies: {summary['applies'].sum():,} "
      f"| Hires: {summary['hires'].sum():,}")
print("\nTop 3 partners by cost per apply:")
print(summary.head(3)[["partner", "cost_per_apply", "apply_rate"]].to_string(index=False))
print("\nBottom 3 partners by cost per apply:")
print(summary.tail(3)[["partner", "cost_per_apply", "apply_rate"]].to_string(index=False))

type_summary = add_kpis(df.groupby("partner_type", as_index=False)[
    ["spend_usd", "clicks", "applies", "hires"]].sum()).round(3)
print("\nBy partner type:")
print(type_summary[["partner_type", "spend_usd", "cost_per_apply", "cost_per_hire"]]
      .sort_values("cost_per_apply").to_string(index=False))

poor = summary[summary["recommendation"] == "Review/Pause"]
share = poor["spend_usd"].sum() / total_spend * 100
print(f"\n{len(poor)} partners flagged 'Review/Pause' hold {share:.1f}% of total spend.")
print("Budget reallocation opportunity: shift part of that spend to 'Scale' partners.")

region_summary = add_kpis(df.groupby("region", as_index=False)[
    ["spend_usd", "clicks", "applies", "hires"]].sum()).round(3)
print("\nBy region:")
print(region_summary[["region", "cost_per_apply", "apply_rate"]].to_string(index=False))

# ---------- 5. Charts ----------
colors = {"Scale": "#2e7d32", "Optimize": "#f9a825", "Review/Pause": "#c62828"}

# Chart 1: cost per apply by partner
s = summary.sort_values("cost_per_apply", ascending=False)
plt.figure(figsize=(9, 6))
plt.barh(s["partner"], s["cost_per_apply"], color=s["recommendation"].map(colors))
plt.axvline(med_cpa, color="black", linestyle="--", linewidth=1, label="Median")
plt.xlabel("Cost per apply (USD)")
plt.title("Cost per Apply by Partner (green = Scale, red = Review/Pause)")
plt.legend()
plt.tight_layout()
plt.savefig("charts/cost_per_apply_by_partner.png", dpi=150)
plt.close()

# Chart 2: spend vs apply rate
plt.figure(figsize=(8, 6))
for rec, g in summary.groupby("recommendation"):
    plt.scatter(g["spend_usd"], g["apply_rate"] * 100, s=90, label=rec, color=colors[rec])
for _, r in summary.iterrows():
    plt.annotate(r["partner"], (r["spend_usd"], r["apply_rate"] * 100), fontsize=7,
                 xytext=(4, 4), textcoords="offset points")
plt.xlabel("Total spend (USD)")
plt.ylabel("Apply rate (%)")
plt.title("Spend vs Apply Rate by Partner")
plt.legend()
plt.tight_layout()
plt.savefig("charts/spend_vs_apply_rate.png", dpi=150)
plt.close()

# Chart 3: monthly trend of cost per apply by partner type
m = df.groupby(["month", "partner_type"], as_index=False)[["spend_usd", "applies"]].sum()
m["cost_per_apply"] = m["spend_usd"] / m["applies"]
plt.figure(figsize=(9, 5))
for t, g in m.groupby("partner_type"):
    plt.plot(g["month"], g["cost_per_apply"], marker="o", label=t)
plt.ylabel("Cost per apply (USD)")
plt.title("Monthly Cost per Apply by Partner Type")
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig("charts/monthly_trend_by_type.png", dpi=150)
plt.close()

print("\nSaved charts to charts/ and summary to data/partner_summary.csv")
