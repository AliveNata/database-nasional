-- Skema inti, Postgres biasa (tanpa PostGIS).
-- Jalankan sekali: psql -d bengkel -f db/schema.sql
create table if not exists ref_kecamatan (
  kode_kec   text primary key,
  kecamatan  text not null,
  kode_kab   text not null,
  kabupaten  text not null,
  kode_prov  text not null,
  provinsi   text not null
);

-- Hasil mentah scraper, apa adanya. Satu tempat bisa muncul berkali-kali dari
-- kecamatan atau keyword berbeda; dedup dilakukan di tahap cleaning.
create table if not exists raw_places (
  id             bigserial primary key,
  place_id       text,
  cid            text,
  query_kode_kec text,
  query_kategori text,
  title          text,
  category       text,
  address        text,
  phone          text,
  website        text,
  latitude       double precision,
  longitude      double precision,
  status         text,
  raw            jsonb,
  scraped_at     timestamptz not null default now()
);
create index if not exists raw_places_place_idx on raw_places (place_id);

-- Progres per kecamatan+kategori, biar run bisa dilanjut kalau putus.
create table if not exists scrape_progress (
  kode_kec   text not null,
  kategori   text not null,
  status     text not null default 'done',
  places     integer not null default 0,
  updated_at timestamptz not null default now(),
  primary key (kode_kec, kategori)
);

-- Hasil bersih siap export.
create table if not exists clean_bengkel (
  place_id        text primary key,
  nama            text not null,
  alamat          text,
  no_hp           text,
  kecamatan       text,
  kabupaten       text,
  provinsi        text,
  kode_kec        text,
  latitude        double precision,
  longitude       double precision,
  kategori        text,
  koordinat_valid boolean not null default true,
  sumber_wilayah  text not null default 'query',
  updated_at      timestamptz not null default now()
);
