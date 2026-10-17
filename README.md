# Data Engineering Toolkit

Small, tested helpers for data pipelines.

## silent_failure_checks.py
Five checks for a pipeline that finishes "Success" but may still be wrong:
row count, duplicates, null rate, freshness and schema drift.

Run it: `python silent_failure_checks.py`
It prints one passing dataset and one broken dataset with the problems found.# data-engineering-toolkit
