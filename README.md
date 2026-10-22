# Data Engineering Toolkit

Small, tested helpers for data pipelines.

## silent_failure_checks.py
Five checks for a pipeline that finishes "Success" but may still be wrong:
row count, duplicates, null rate, freshness and schema drift.

Run it: `python silent_failure_checks.py`
It prints one passing dataset and one broken dataset with the problems found.# data-engineering-toolkit

## Test set
- 30 answerable questions, each with the arXiv id of the paper that answers it.
- 10 should-refuse questions, written from database papers deliberately left out of the index. Each was checked against the index by keyword search; 6 candidates were replaced over 3 rounds because the index could already answer them.
- Questions were drafted with AI assistance from random samples of abstracts, then checked against the data by me.
