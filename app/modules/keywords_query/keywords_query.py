"""Keyword request lookup backed by an externally provisioned dataset.

The production CSV is deliberately not distributed in the public Git repository.
Set WB_KEYWORD_REQUESTS_CSV_PATH to a trusted local CSV path, or provision
requests.csv alongside this module in a private environment.
"""
import os
from pathlib import Path

import pandas as pd

DEFAULT_CSV = Path(__file__).resolve().parent / "requests.csv"
csv_path = Path(os.environ.get("WB_KEYWORD_REQUESTS_CSV_PATH", str(DEFAULT_CSV)))

if csv_path.is_file():
    df = pd.read_csv(csv_path, header=None, names=["keyword", "query"])
    queries_dict = df.set_index("keyword")["query"].to_dict()
    del df
else:
    queries_dict = {}

min_query = list(queries_dict.values())[-1] if queries_dict else None


def get_queries_of_keyword(keyword: str) -> int | str:
    if not queries_dict:
        raise RuntimeError(
            "Keyword requests dataset is not configured. "
            "Provide WB_KEYWORD_REQUESTS_CSV_PATH pointing to a private requests.csv."
        )
    if keyword in queries_dict:
        return queries_dict[keyword]
    return f"<{min_query}"
