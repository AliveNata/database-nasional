"""Ubah raw_places jadi clean_bengkel: dedup, tentukan wilayah, rapiin no HP, filter.

Wilayah default diambil dari kecamatan yang diquery (kolom query_kode_kec) lalu
dijoin ke ref_kecamatan. Kalau boundaries.sql dijalankan dan geom terisi, jalankan
spatial_refine.sql terpisah untuk mengoreksi wilayah dari titik lokasi.
"""
from __future__ import annotations

from db import connect
from normalize import is_permanently_closed, normalize_phone

# Kotak batas kasar Indonesia untuk validasi koordinat.
LON_MIN, LON_MAX = 95.0, 141.5
LAT_MIN, LAT_MAX = -11.5, 6.5


def _coord_valid(lat: float | None, lon: float | None) -> bool:
    return (
        lat is not None and lon is not None
        and LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX
    )


def main() -> None:
    with connect() as conn, conn.cursor() as cur:
        # Satu baris per place_id: utamakan yang punya nomor HP, lalu paling baru.
        cur.execute(
            """select distinct on (r.place_id)
                 r.place_id, r.title, r.address, r.phone, r.query_kategori,
                 r.latitude, r.longitude, r.status,
                 k.kecamatan, k.kabupaten, k.provinsi, k.kode_kec
               from raw_places r
               left join ref_kecamatan k on k.kode_kec = r.query_kode_kec
               where r.place_id is not null
               order by r.place_id, (r.phone is not null) desc, r.scraped_at desc"""
        )
        rows = cur.fetchall()

        clean: list[dict[str, object]] = []
        for (place_id, title, address, phone, kategori, lat, lon, status,
             kecamatan, kabupaten, provinsi, kode_kec) in rows:
            if is_permanently_closed(status):
                continue
            if not title:
                continue
            clean.append({
                "place_id": place_id,
                "nama": title,
                "alamat": address,
                "no_hp": normalize_phone(phone),
                "kecamatan": kecamatan,
                "kabupaten": kabupaten,
                "provinsi": provinsi,
                "kode_kec": kode_kec,
                "latitude": lat,
                "longitude": lon,
                "kategori": kategori,
                "koordinat_valid": _coord_valid(lat, lon),
                "sumber_wilayah": "query",
            })

        cur.execute("truncate clean_bengkel")
        cur.executemany(
            """insert into clean_bengkel
               (place_id, nama, alamat, no_hp, kecamatan, kabupaten, provinsi, kode_kec,
                latitude, longitude, kategori, koordinat_valid, sumber_wilayah)
               values (%(place_id)s, %(nama)s, %(alamat)s, %(no_hp)s, %(kecamatan)s,
                %(kabupaten)s, %(provinsi)s, %(kode_kec)s, %(latitude)s, %(longitude)s,
                %(kategori)s, %(koordinat_valid)s, %(sumber_wilayah)s)""",
            clean,
        )
        conn.commit()

    total = len(clean)
    dengan_hp = sum(1 for r in clean if r["no_hp"])
    print(f"clean_bengkel: {total} bengkel (dari {len(rows)} unik place_id)")
    if total:
        print(f"  punya no HP: {dengan_hp} ({dengan_hp * 100 // total}%)")


if __name__ == "__main__":
    main()
