#!/usr/bin/env bash
# Jalankan gosom google-maps-scraper via Docker.
# Contoh:
#   ./run_scrape.sh queries/dki_queries.txt        # tes 1 provinsi dulu
#   ./run_scrape.sh queries/pilot_queries.txt      # full pilot 3 provinsi
# Hasil: scraper/out/results.json (dipakai pipeline/load.py).
set -euo pipefail

QUERIES="${1:-queries/pilot_queries.txt}"
DEPTH="${DEPTH:-10}"
CONC="${CONC:-4}"
INACTIVITY="${INACTIVITY:-5m}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/scraper/out"
PROXIES="$ROOT/scraper/proxies.txt"
mkdir -p "$OUT"

if [[ ! -f "$ROOT/$QUERIES" ]]; then echo "File query tidak ada: $QUERIES"; exit 1; fi

PROXY_ARGS=()
if [[ -f "$PROXIES" ]]; then
  PROXY_ARGS=(-v "$PROXIES:/proxies.txt:ro")
  GOSOM_PROXY=(-proxies-file /proxies.txt)
else
  echo "PERINGATAN: scraper/proxies.txt tidak ada, jalan tanpa proxy (hanya untuk tes 1 kecamatan)."
  GOSOM_PROXY=()
fi

RESUME=()
[[ -f "$OUT/results.json" ]] && RESUME=(-resume)

docker run --rm \
  -e DISABLE_TELEMETRY=1 \
  -v gmaps-playwright-cache:/opt \
  -v "$ROOT/$QUERIES:/queries.txt:ro" \
  -v "$OUT:/out" \
  "${PROXY_ARGS[@]}" \
  gosom/google-maps-scraper \
  -input /queries.txt \
  -results /out/results.json -json \
  -lang id -depth "$DEPTH" -c "$CONC" \
  "${GOSOM_PROXY[@]}" "${RESUME[@]}" \
  -exit-on-inactivity "$INACTIVITY"

echo "Selesai. Hasil di $OUT/results.json"
