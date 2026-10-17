"""
Five checks for a pipeline that finishes with status "Success" but may still be wrong.
Pandas version so you can run it anywhere; the same logic ports to PySpark.
"""
import pandas as pd

def run_checks(df, key, ts_col, expected_cols, expected_rows, row_tolerance=0.02,
               max_null_rate=0.05, max_age_hours=24, now=None):
    now = now or pd.Timestamp.now()
    problems = []

    # 1) Completeness: row count vs what the source said it sent
    low, high = expected_rows * (1 - row_tolerance), expected_rows * (1 + row_tolerance)
    if not (low <= len(df) <= high):
        problems.append(f"ROW COUNT: got {len(df)}, expected about {expected_rows}")

    # 2) Duplicates on the business key
    dups = int(df.duplicated(subset=key).sum())
    if dups:
        problems.append(f"DUPLICATES: {dups} rows repeat the key {key}")

    # 3) Null rate per column
    for col, rate in df.isna().mean().items():
        if rate > max_null_rate:
            problems.append(f"NULLS: {col} is {rate:.0%} null (limit {max_null_rate:.0%})")

    # 4) Freshness
    newest = pd.to_datetime(df[ts_col]).max()
    age_h = (now - newest).total_seconds() / 3600
    if age_h > max_age_hours:
        problems.append(f"STALE: newest {ts_col} is {age_h:.0f} hours old (limit {max_age_hours})")

    # 5) Schema drift
    missing = set(expected_cols) - set(df.columns)
    extra = set(df.columns) - set(expected_cols)
    if missing: problems.append(f"SCHEMA: missing columns {sorted(missing)}")
    if extra: problems.append(f"SCHEMA: unexpected columns {sorted(extra)}")

    return problems

if __name__ == "__main__":
    now = pd.Timestamp("2026-10-16 09:00")
    good = pd.DataFrame({"order_id": range(1000), "amount": 10.0,
                         "updated_at": pd.Timestamp("2026-10-16 02:00")})
    print("Good data    :", run_checks(good, ["order_id"], "updated_at",
          ["order_id", "amount", "updated_at"], expected_rows=1000, now=now) or "all checks passed")

    bad = pd.concat([good.iloc[:780], good.iloc[:20]]).reset_index(drop=True)   # lost 22% of rows, 20 duplicates
    bad.loc[:200, "amount"] = None                                              # nulls
    bad["updated_at"] = pd.Timestamp("2026-10-13 02:00")                        # stale
    bad = bad.rename(columns={"amount": "amt"})                                 # schema drift
    for p in run_checks(bad, ["order_id"], "updated_at",
                        ["order_id", "amount", "updated_at"], expected_rows=1000, now=now):
        print("Broken data  :", p)
