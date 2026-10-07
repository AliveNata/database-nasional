# National Auto Repair Shop Data Pipeline

> ** Disclaimer:** This repository contains a proprietary data pipeline (ETL) created for a specific client. It is published here strictly for portfolio and demonstration purposes. No license is granted for reproduction, modification, or reuse.

## Project Overview
An automated Data Engineering pipeline designed to extract, clean, normalize, and export Google Business Profile data for auto repair workshops (bengkel) across Indonesia. 

Raw geographical and business data is often unstructured and messy. This project solves that by transforming raw scrapes into a structured, relational format using PostgreSQL, and ultimately generating clean, formatted Excel reports for client deliverables.

## Tech Stack & Tools
* **Language:** Python 3
* **Database:** PostgreSQL
* **Libraries:** `pandas`, `openpyxl`, `psycopg2`, `re` (Regex)
* **Architecture:** ETL (Extract, Transform, Load)

## Key Features & Pipeline Architecture

### 1. Extraction (Data Scraping & Ingestion)
* Ingests raw JSON data from Google Maps / Places API into a staging database table (`raw_places`).
* Handles pagination and proxy rotation to ensure comprehensive coverage across multiple provinces and districts (Kecamatan/Kabupaten).

### 2. Transformation (Data Cleaning & Normalization)
* **Regex Filtering:** Automatically detects and categorizes specific repair services (e.g., "Cat/Repair") based on complex regex patterns matching business names (e.g., *body, bodi, ketok, dempul*).
* **Data Sanitization:** Strips out generic placeholders (e.g., businesses named simply "Bengkel Mobil" without an actual brand name) to maintain data quality.
* **Categorization Mapping:** Splits raw Google categories into 'Primary' and 'Secondary' tags. Falls back to predefined lists if the primary category matches standard target services (like *Oil Change Service* or *Motorcycle Repair*).
* **Address Parsing:** Analyzes address completeness, identifying whether an entry contains a full street address, a Plus Code, or just a region name.

### 3. Load (Automated Reporting)
* Executes complex SQL joins and aggregations to fetch the most up-to-date observation per business ID.
* Dynamically generates Excel files using `openpyxl`.
* Forces text-formatting on phone numbers (to retain leading zeros) and sanitizes spreadsheet formulas (escaping `=`, `+`, `-`, `@`) to prevent Excel errors.
* Applies custom styling, frozen panes, and auto-filters for a polished final deliverable.

## Author
**Alief Akbar | [AlyxLabs](https://alyxlabs.tech)**
