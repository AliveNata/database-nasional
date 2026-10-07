"""Pembersihan nomor HP dan kategori, murni tanpa efek samping supaya gampang ditest."""
from __future__ import annotations

import re

_DIGITS = re.compile(r"\d+")
# Status Google Maps yang dianggap tutup permanen dan dibuang.
CLOSED_PERMANENTLY = {"closed_permanently", "permanently_closed"}


def normalize_phone(raw: str | None) -> str | None:
    """Ubah satu atau beberapa nomor jadi format 08xx. Ambil nomor valid pertama.

    Google Maps mengembalikan nomor dalam banyak bentuk: '+62 21 1234567',
    '0812-3456-7890', '(021) 7654321', kadang beberapa dipisah '/' atau ','.
    Kembalikan None kalau tidak ada nomor yang masuk akal.
    """
    if not raw:
        return None
    for candidate in re.split(r"[/,;]| atau ", raw):
        digits = "".join(_DIGITS.findall(candidate))
        if not digits:
            continue
        if digits.startswith("62"):
            digits = "0" + digits[2:]
        elif not digits.startswith("0"):
            digits = "0" + digits
        # Nomor Indonesia yang wajar: 9 sampai 14 digit termasuk 0 di depan.
        if 9 <= len(digits) <= 14:
            return digits
    return None


def is_permanently_closed(status: str | None) -> bool:
    return (status or "").strip().lower().replace(" ", "_") in CLOSED_PERMANENTLY


def parse_input_id(input_id: str | None) -> tuple[str | None, str | None]:
    """input_id berformat 'kode_kec|kategori', mis. '31.71.01|mobil'."""
    if not input_id or "|" not in input_id:
        return (input_id or None, None)
    kode, kategori = input_id.split("|", 1)
    kode = kode.strip() or None
    kategori = kategori.strip().lower() or None
    if kategori not in {"mobil", "motor"}:
        kategori = None
    return (kode, kategori)
