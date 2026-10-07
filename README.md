# Database Bengkel Nasional

Pipeline untuk mengumpulkan data bengkel mobil dan motor dari Google Maps, membersihkannya, dan mengekspor ke Excel. Tahap pertama adalah pilot 3 provinsi (DKI Jakarta, Jawa Barat, Banten), lalu dilanjutkan nasional.

Scraping dijalankan sebagai job background di VM, bukan di sesi AI. Sesi AI atau Claude Code dipakai untuk setup, memantau, lalu cleaning dan export.

## Alur ringkas

1. Data wilayah: daftar kecamatan (kode BPS) sudah tersedia di `data/kecamatan/kecamatan_ref.csv`.
2. Generate query: kecamatan dikali keyword jadi file input untuk scraper.
3. Scraping: gosom google-maps-scraper lewat proxy Decodo IP Indonesia, hasil ke JSON.
4. Load: hasil JSON dimasukkan ke Postgres (tabel raw_places).
5. Cleaning: dedup per place_id, tentukan wilayah, rapikan no HP, buang yang tutup permanen.
6. Export: file Excel siap kirim ke klien.

## Struktur folder

```
data/kecamatan/kecamatan_ref.csv   referensi kecamatan 3 provinsi (826 kecamatan)
scraper/gen_queries.py             bikin file query dari referensi
scraper/run_scrape.sh              wrapper Docker untuk gosom
scraper/proxies.example.txt        contoh isi proxy Decodo
queries/                           file query hasil generate
db/schema.sql                      skema Postgres inti
db/boundaries.sql                  opsional, PostGIS untuk batas wilayah
pipeline/load_ref.py               muat referensi kecamatan ke Postgres
pipeline/load.py                   muat hasil scraper ke raw_places
pipeline/clean.py                  raw_places jadi clean_bengkel
pipeline/export_excel.py           clean_bengkel jadi Excel
pipeline/normalize.py              logika no HP dan kategori (ada test)
export/                            output Excel
```

## Prasyarat di VM

- Docker (untuk gosom)
- Postgres (pakai yang sudah ada di VM)
- Python 3.10 ke atas
- Akun Decodo dengan proxy IP Indonesia

## Langkah pengerjaan

### 0. Siapkan Python dan database

```bash
cd database-nasional
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env            # isi DATABASE_URL ke Postgres di VM

createdb bengkel     # kalau database belum ada
psql "$DATABASE_URL" -f db/schema.sql
python pipeline/load_ref.py    # muat 826 kecamatan ke ref_kecamatan
```

### 1. Daftar Decodo dan isi proxy

1. Daftar di decodo.com, aktifkan Residential Proxies (ada trial 100 MB untuk ukur pemakaian).
2. Di dashboard, pilih lokasi Indonesia, salin endpoint dan kredensialnya.
3. Salin `scraper/proxies.example.txt` menjadi `scraper/proxies.txt`, isi endpoint tadi. File ini tidak di-commit.

### 2. Tes kecil dulu untuk ukur pemakaian GB

Jalankan satu provinsi kecil dulu (DKI, 44 kecamatan) untuk melihat berapa GB proxy yang terpakai sebelum lari full.

```bash
python scraper/gen_queries.py --provinsi 31 --out queries/dki_queries.txt
bash scraper/run_scrape.sh queries/dki_queries.txt
```

Setelah selesai, cek pemakaian GB di dashboard Decodo. Perkiraan pemakaian nasional kira kira pemakaian ini dikali rasio jumlah kecamatan.

### 3. Full pilot 3 provinsi

```bash
python scraper/gen_queries.py                 # 826 kecamatan x 2 keyword = 1652 query
# jalankan sebagai background job supaya aman kalau terminal putus:
screen -S scrape
bash scraper/run_scrape.sh queries/pilot_queries.txt
# tekan Ctrl-A lalu D untuk detach, screen -r scrape untuk balik
```

Kalau run putus, jalankan perintah yang sama lagi. Scraper melanjutkan dari hasil yang sudah ada (mode resume otomatis kalau `scraper/out/results.json` sudah ada).

### 4. Load, cleaning, export

```bash
python pipeline/load.py scraper/out/results.json
python pipeline/clean.py
python pipeline/export_excel.py
```

File Excel muncul di `export/bengkel_<tanggal>.xlsx` dengan kolom nama, alamat, no HP, kecamatan, kabupaten, provinsi, latitude, longitude, kategori. No HP disimpan sebagai teks supaya angka 0 di depan tidak hilang, header diberi filter, baris pertama dibekukan.

## Keyword dan cakupan

Default pakai 2 keyword inti (`bengkel mobil`, `bengkel motor`) untuk menghemat GB. Untuk cakupan lebih luas, tambahkan varian servis:

```bash
python scraper/gen_queries.py --extended       # jadi 4 keyword
```

Kategori mobil atau motor ditentukan dari keyword yang dipakai, bukan dari kategori Google Maps.

## Menentukan wilayah dari titik lokasi (opsional)

Secara default wilayah diambil dari kecamatan yang diquery, lalu dijoin ke referensi untuk mendapatkan kabupaten dan provinsi. Ini akurat untuk sebagian besar bengkel, tetapi bengkel di dekat perbatasan bisa masuk kecamatan tetangga.

Untuk mengoreksi wilayah dari titik koordinat, muat polygon batas kecamatan (dari OSM) dan aktifkan PostGIS:

```bash
psql "$DATABASE_URL" -f db/boundaries.sql
# lalu muat polygon batas kecamatan ke ref_kecamatan.geom (langkah ini belum otomatis)
```

Ini peningkatan, bukan syarat untuk pilot.

## Batasan data

- Data diambil dari bengkel yang terdaftar di Google Maps. Bengkel tanpa listing tidak ikut terambil.
- No HP diambil sesuai yang tersedia di listing. Bengkel tanpa nomor tetap masuk dengan kolom No HP kosong.
- Bengkel berstatus tutup permanen dibuang.
- Koordinat mengikuti titik di Google Maps. Titik yang jelas salah (di luar wilayah Indonesia) dikosongkan di Excel, tetapi barisnya tetap ada.
- Scraping Google Maps melanggar ToS Google. Umum dilakukan, konsekuensi yang biasa adalah blokir IP, bukan tuntutan. Jangan cantumkan sumber Google Maps di invoice atau kontrak.

## Test

```bash
cd pipeline && python -m pytest test_normalize.py -q
```

Menguji normalisasi no HP, deteksi tutup permanen, dan parsing input_id.
