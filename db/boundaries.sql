-- OPSIONAL: aktifkan penentuan wilayah dari titik (spatial join).
-- Butuh PostGIS dan polygon batas kecamatan dimuat ke ref_kecamatan.geom.
-- Kalau ini tidak dijalankan, wilayah diambil dari kecamatan yang diquery.
create extension if not exists postgis;
alter table ref_kecamatan add column if not exists geom geometry(multipolygon, 4326);
create index if not exists ref_kecamatan_geom_idx on ref_kecamatan using gist (geom);
