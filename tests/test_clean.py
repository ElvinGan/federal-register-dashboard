from datetime import date

from fetch_data import clean, month_ranges


def doc(**kw):
    base = {"document_number": "2026-00001", "publication_date": "2026-09-01", "type": "Notice",
            "title": "A title", "agency_names": ["Commerce Department"], "page_length": 3}
    return {**base, **kw}


def test_duplicates_and_incomplete_rows_are_dropped():
    rows = clean([doc(), doc(), doc(document_number="2026-00002", publication_date=None),
                  doc(document_number="2026-00003", type=None)])
    assert [r["document_number"] for r in rows] == ["2026-00001"]


def test_title_whitespace_and_missing_agency():
    row = clean([doc(title="  Two\n  lines  ", agency_names=[], page_length=None)])[0]
    assert row["title"] == "Two lines"
    assert row["agency"] == "Unknown"
    assert row["pages"] == 0


def test_month_ranges_split_on_month_boundaries():
    assert list(month_ranges(date(2026, 1, 15), date(2026, 3, 10))) == [
        (date(2026, 1, 15), date(2026, 1, 31)),
        (date(2026, 2, 1), date(2026, 2, 28)),
        (date(2026, 3, 1), date(2026, 3, 10)),
    ]
