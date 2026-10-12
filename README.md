# Federal Register dashboard

Pulls documents from the [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1)
(rules, proposed rules, notices and presidential documents) and shows them in a small dashboard:
documents per week, top 10 agencies and document length, with a filter for document type.

The API is public and needs no key.

## Run it

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python fetch_data.py          # optional, a CSV for Apr-Sep 2026 is already in data/
    python -m http.server 8000

Then open http://localhost:8000. The page loads `data/documents.csv`, so it has to be served
over http (opening the file directly is blocked by the browser). Chart.js and PapaParse load from cdnjs.

`fetch_data.py` takes `--start`, `--end` (YYYY-MM-DD) and `--out`. The default range is the last six
full months. It fetches month by month because the API stops at 10,000 results per query.

## About the data

- One row per document: number, publication date, type, agency, title, pages.
- Cleaning: duplicates and rows with no date or type are dropped, titles are tidied, and when a
  document lists several agencies only the first (the lead agency) is kept.
- The bundled CSV has 13,427 documents from 1 Apr to 30 Sep 2026.

## Tests

    pytest
