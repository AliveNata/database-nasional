"""Muat data/kecamatan/kecamatan_ref.csv ke tabel ref_kecamatan."""
from __future__ import annotations

import csv
from pathlib import Path

from db import connect

REF = Path(__file__).resolve().parent.parent / "data" / "kecamatan" / "kecamatan_ref.csv"


def main() -> None:
    with REF.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with connect() as conn, conn.cursor() as cur:
        cur.executemany(
            """insert into ref_kecamatan (kode_kec, kecamatan, kode_kab, kabupaten, kode_prov, provinsi)
               values (%(kode_kec)s, %(kecamatan)s, %(kode_kab)s, %(kabupaten)s, %(kode_prov)s, %(provinsi)s)
               on conflict (kode_kec) do update set
                 kecamatan = excluded.kecamatan, kabupaten = excluded.kabupaten, provinsi = excluded.provinsi""",
            rows,
        )
        conn.commit()
    print(f"{len(rows)} kecamatan dimuat ke ref_kecamatan")


if __name__ == "__main__":
    main()
