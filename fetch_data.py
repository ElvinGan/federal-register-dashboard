"""Download Federal Register documents for a date range and save a cleaned CSV.

Uses the public API at federalregister.gov/api/v1 (no key needed).
Usage: python fetch_data.py [--start 2026-04-01] [--end 2026-09-30] [--out data/documents.csv]
"""
import argparse
import csv
import re
import time
from datetime import date, timedelta

import requests

API = "https://www.federalregister.gov/api/v1/documents.json"
FIELDS = ["document_number", "publication_date", "type", "title", "agency_names", "page_length"]
COLUMNS = ["document_number", "publication_date", "type", "agency", "title", "pages"]


def fetch_month(session, start, end):
    """All documents published between two dates. The API caps a query at 10,000 results,
    so we ask for one month at a time."""
    params = {
        "conditions[publication_date][gte]": start,
        "conditions[publication_date][lte]": end,
        "fields[]": FIELDS,
        "per_page": 1000,
        "order": "oldest",
    }
    rows, page = [], 1
    while True:
        r = session.get(API, params={**params, "page": page}, timeout=60)
        r.raise_for_status()
        data = r.json()
        rows += data["results"]
        if page >= data.get("total_pages", 1):
            return rows
        page += 1
        time.sleep(0.5)


def clean(raw_rows):
    """Drop duplicates and rows missing a date or type, tidy the text, keep the lead agency."""
    seen, out = set(), []
    for r in raw_rows:
        num = r.get("document_number")
        if not num or num in seen or not r.get("publication_date") or not r.get("type"):
            continue
        seen.add(num)
        agencies = r.get("agency_names") or []
        out.append({
            "document_number": num,
            "publication_date": r["publication_date"],
            "type": r["type"].strip(),
            "agency": agencies[0].strip() if agencies else "Unknown",
            "title": re.sub(r"\s+", " ", r.get("title") or "").strip(),
            "pages": r.get("page_length") or 0,
        })
    return out


def month_ranges(start, end):
    d = start.replace(day=1)
    while d <= end:
        nxt = (d + timedelta(days=32)).replace(day=1)
        yield max(d, start), min(nxt - timedelta(days=1), end)
        d = nxt


def default_range():
    first_of_this_month = date.today().replace(day=1)
    end = first_of_this_month - timedelta(days=1)
    start = end.replace(day=1)
    for _ in range(5):  # six full months in total
        start = (start - timedelta(days=1)).replace(day=1)
    return start, end


def main():
    s, e = default_range()
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=date.fromisoformat, default=s)
    ap.add_argument("--end", type=date.fromisoformat, default=e)
    ap.add_argument("--out", default="data/documents.csv")
    args = ap.parse_args()

    session = requests.Session()
    session.headers["User-Agent"] = "federal-register-dashboard (portfolio project)"
    raw = []
    for a, b in month_ranges(args.start, args.end):
        month = fetch_month(session, a.isoformat(), b.isoformat())
        print(f"{a:%Y-%m}: {len(month)} documents")
        raw += month

    rows = clean(raw)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
