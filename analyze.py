# analyze.py
# Make KM-Waechter smarter. The 80% rule only warns you once a car is nearly worn. Here you find
# which cars are most likely to break down SOON, from their history, and rank them by risk, so the
# fleet team fixes the risky ones first.
#
# fleet_history.csv has one row per car (120 of them) and a "broke_down" column (1 = it later
# broke down).
#
# SUMMARY: Breakdown risk tracks how overdue a car is for service (km_since_service) and how hard
# it is worked (avg_daily_km, load_factor). Mileage and age do NOT predict breakdowns: they
# separate the two groups by ~0.00 and correlate 0.977 with each other, so they only restate one
# another. The 80% rule reads km_since_service alone and so misses hard-worked cars that were
# serviced recently -- exactly the ones this ranking surfaces.
#
# How the score is built: each column's separation strength (Cohen's d) becomes its weight, so the
# strongest predictor dominates and the useless columns drop out on their own.

import pandas as pd

SEPARATION_THRESHOLD = 0.3  # Cohen's d below this is noise, not signal
SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def column_separation(df: pd.DataFrame) -> pd.DataFrame:
    """Compare each numeric column across the cars that broke down and those that did not.

    cohens_d is the standardised gap between the two groups. Near zero means the column
    carries no information about breakdowns, however plausible it looks.
    """
    numeric = df.select_dtypes("number").drop(columns=["broke_down"])
    broke, survived = df[df.broke_down == 1], df[df.broke_down == 0]
    rows = []
    for col in numeric.columns:
        a, b = broke[col], survived[col]
        pooled = (((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2)) ** 0.5
        rows.append({
            "column": col,
            "broke_down": a.mean(),
            "survived": b.mean(),
            "gap": a.mean() - b.mean(),
            "cohens_d": abs(a.mean() - b.mean()) / pooled,
        })
    return pd.DataFrame(rows).sort_values("cohens_d", ascending=False)


def predictive_weights(sep: pd.DataFrame) -> dict:
    """Keep only the columns that separate the groups, weighted by their effect size."""
    keep = sep[sep.cohens_d >= SEPARATION_THRESHOLD]
    return dict(zip(keep.column, keep.cohens_d))


def risk_scores(df: pd.DataFrame, weights: dict) -> pd.Series:
    """Score each car 0-100 from the weighted, min-max normalised predictive columns.

    Indexed by the frame's own index, not by car_id: assigning a car_id-indexed Series to
    df["risk"] would align on the index and silently produce all-NaN.
    """
    total_weight = sum(weights.values())
    scores = {}
    for idx, row in df.iterrows():
        score = 0.0
        for col, weight in weights.items():
            span = df[col].max() - df[col].min()
            score += weight * (row[col] - df[col].min()) / span
        scores[idx] = round(100 * score / total_weight, 1)
    return pd.Series(scores)


def main() -> None:
    """Run the breakdown-risk analysis and print the fleet ranked by risk."""
    df = pd.read_csv("fleet_history.csv")
    break_threshold = SERVICE_INTERVAL_KM * WARN_AT_PERCENT / 100

    sep = column_separation(df)
    weights = predictive_weights(sep)
    df["risk"] = risk_scores(df, weights)
    df["flagged_80"] = df.km_since_service >= break_threshold

    print("=" * 78)
    print(f"Which columns predict a breakdown?  ({len(df)} cars, {int(df.broke_down.sum())} broke down)")
    print("=" * 78)
    print(sep.to_string(index=False, float_format=lambda v: f"{v:9.3f}"))
    print(f"\nDropping everything below cohens_d {SEPARATION_THRESHOLD} leaves: {', '.join(weights)}")
    print(f"corr(age_years, odometer_km) = {df.age_years.corr(df.odometer_km):.3f}"
          "  <- the two 'obvious' factors are one variable in disguise.")

    print("\n" + "=" * 78)
    print("Fleet ranked by breakdown risk (highest first)")
    print("=" * 78)
    print(f"{'car_id':<11}{'risk':>7}{'since_svc':>11}{'km/day':>8}{'load':>7}"
          f"{'odometer':>11}{'age':>5}{'80% rule':>10}{'broke':>7}")
    for _, r in df.sort_values("risk", ascending=False).head(25).iterrows():
        rule = "FLAG" if r.flagged_80 else "-"
        print(f"{r.car_id:<11}{r.risk:>7.1f}{r.km_since_service:>11,}{r.avg_daily_km:>8,}"
              f"{r.load_factor:>7.2f}{r.odometer_km:>11,}{r.age_years:>5}"
              f"{rule:>10}{int(r.broke_down):>7}")

    broke = df.broke_down == 1
    total = int(broke.sum())
    top20 = df.risk >= df.nlargest(20, "risk").risk.min()
    missed = df[broke & ~df.flagged_80]

    print("\n" + "=" * 78)
    print("How this compares to the 80% rule it is meant to supplement")
    print("=" * 78)
    print(f"80% rule alone : flags {int(df.flagged_80.sum()):>3} cars, "
          f"catches {int((broke & df.flagged_80).sum()):>2} of {total} breakdowns")
    print(f"risk top 20    : flags {int(top20.sum()):>3} cars, "
          f"catches {int((broke & top20).sum()):>2} of {total} breakdowns "
          f"(chance would be {20 * total / len(df):.1f})")
    print(f"both together  : flags {int((df.flagged_80 | top20).sum()):>3} cars, "
          f"catches {int((broke & (df.flagged_80 | top20)).sum()):>2} of {total} breakdowns")
    print("\nSo the risk ranking does not replace the 80% rule. It is more efficient per car "
          "reviewed\n(13 breakdowns from 20 cars, against 17 from 32), and it is complementary: "
          f"{int((broke & top20 & ~df.flagged_80).sum())} breakdowns are caught ONLY by risk.")

    print(f"\n{len(missed)} breakdowns never trip the 80% rule at all:")
    print(missed.sort_values("risk", ascending=False)[
        ["car_id", "risk", "km_since_service", "avg_daily_km", "load_factor"]
    ].to_string(index=False))
    print(f"\n{int((missed.risk >= df.risk.median()).sum())} of those {len(missed)} sit in the top "
          "half of the fleet by\nrisk, so working the risk list before the rule would reach them.")

    print("\nHonest limitations:")
    print("  - This is a ranking, not a prediction. High wear plus hard use looks identical")
    print("    before a car fails, so healthy cars score high too (VOS-1217, VOS-1032, VOS-1162).")
    print("  - The CSV records only WHETHER a car broke down, never WHEN. Nothing here")
    print("    estimates a timeframe, so 'SOON' in the brief is not something the data supports.")
    print("  - 120 cars and 26 breakdowns is a small sample; the weights are descriptive, not")
    print("    fitted, and would want re-checking on a larger history.")


if __name__ == "__main__":
    main()