"""Muat hasil gosom (JSON array atau JSONL) ke tabel raw_places."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterator

from db import connect
from normalize import parse_input_id


def _iter_records(path: Path) -> Iterator[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return
    if text[0] == "[":
        yield from json.loads(text)
    else:
        for line in text.splitlines():  # JSONL
            line = line.strip()
            if line:
                yield json.loads(line)


def _num(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path, help="file hasil gosom (.json / .jsonl)")
    args = parser.parse_args()

    rows = []
    for rec in _iter_records(args.results):
        kode_kec, kategori = parse_input_id(rec.get("input_id"))
        rows.append({
            "place_id": rec.get("place_id"),
            "cid": rec.get("cid"),
            "query_kode_kec": kode_kec,
            "query_kategori": kategori,
            "title": rec.get("title"),
            "category": rec.get("category"),
            "address": rec.get("complete_address") or rec.get("address"),
            "phone": rec.get("phone"),
            "website": rec.get("website"),
            "latitude": _num(rec.get("latitude")),
            "longitude": _num(rec.get("longitude")),
            "status": rec.get("status"),
            "raw": json.dumps(rec, ensure_ascii=False),
        })

    with connect() as conn, conn.cursor() as cur:
        cur.executemany(
            """insert into raw_places
               (place_id, cid, query_kode_kec, query_kategori, title, category, address,
                phone, website, latitude, longitude, status, raw)
               values (%(place_id)s, %(cid)s, %(query_kode_kec)s, %(query_kategori)s, %(title)s,
                %(category)s, %(address)s, %(phone)s, %(website)s, %(latitude)s, %(longitude)s,
                %(status)s, %(raw)s)""",
            rows,
        )
        conn.commit()
    print(f"{len(rows)} baris dimuat ke raw_places dari {args.results.name}")


if __name__ == "__main__":
    main()
