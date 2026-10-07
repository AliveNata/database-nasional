"""Bikin file query untuk gosom dari data/kecamatan/kecamatan_ref.csv.

Tiap baris: '<keyword> <kecamatan>, <kabupaten>, <provinsi> #!#<kode_kec>|<kategori>'
input_id (setelah #!#) dipakai loader untuk tahu kecamatan dan kategori tiap hasil.

Pakai:
  python gen_queries.py                       # keyword inti (2), hemat GB
  python gen_queries.py --extended            # tambah varian 'servis'
  python gen_queries.py --provinsi 31         # batasi 1 provinsi (mis. tes)
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REF = BASE / "data" / "kecamatan" / "kecamatan_ref.csv"
OUT = BASE / "queries" / "pilot_queries.txt"

# (keyword, kategori). Keyword inti dulu untuk ukur pemakaian GB, baru extended.
CORE = [("bengkel mobil", "mobil"), ("bengkel motor", "motor")]
EXTENDED = [("servis mobil", "mobil"), ("servis motor", "motor")]

PROV_LABEL = {"31": "DKI Jakarta", "32": "Jawa Barat", "36": "Banten"}


def location(row: dict[str, str]) -> str:
    kab = row["kabupaten"].replace(" Administrasi", "")
    prov = PROV_LABEL.get(row["kode_prov"], row["provinsi"])
    return f"{row['kecamatan']}, {kab}, {prov}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extended", action="store_true", help="tambah keyword 'servis'")
    parser.add_argument("--provinsi", help="filter kode provinsi, mis. 31")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    keywords = CORE + (EXTENDED if args.extended else [])
    with REF.open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if not args.provinsi or r["kode_prov"] == args.provinsi]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for row in rows:
            loc = location(row)
            for keyword, kategori in keywords:
                f.write(f"{keyword} {loc} #!#{row['kode_kec']}|{kategori}\n")

    print(f"{len(rows)} kecamatan x {len(keywords)} keyword = {len(rows) * len(keywords)} query")
    print(f"ditulis ke {args.out}")


if __name__ == "__main__":
    main()
