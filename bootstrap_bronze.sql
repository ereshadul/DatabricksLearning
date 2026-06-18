-- bootstrap_bronze.sql
-- ----------------------
-- Pure-SQL alternative to load_to_databricks.py. Use this if you'd rather
-- not run Python at all, or if your Free Edition account can't generate a
-- personal access token.
--
-- BEFORE running this:
--   1. In the workspace sidebar: Catalog -> Create catalog -> name it
--      "globaltrader" (skip this if you already ran the Python script).
--   2. Inside it, create schemas "bronze", "silver", "gold".
--   3. Inside the bronze schema, create a Volume named "landing".
--   4. Open the "landing" volume and upload all 7 files from /data
--      (drag-and-drop, or Catalog Explorer -> Add data -> Upload files
--      to a volume).
--
-- THEN paste this whole file into a new SQL editor tab or notebook and run
-- it all. End result is identical to the Python script: 5 populated bronze
-- tables, with the incremental batch and the events file sitting in the
-- volume untouched for you to use in Phase 3 and Phase 6.

CREATE CATALOG IF NOT EXISTS globaltrader;
CREATE SCHEMA IF NOT EXISTS globaltrader.bronze;
CREATE SCHEMA IF NOT EXISTS globaltrader.silver;
CREATE SCHEMA IF NOT EXISTS globaltrader.gold;
CREATE VOLUME IF NOT EXISTS globaltrader.bronze.landing;

-- Run the four CREATE TABLE statements below only after the files have
-- actually been uploaded to /Volumes/globaltrader/bronze/landing/

CREATE OR REPLACE TABLE globaltrader.bronze.accounts AS
SELECT *, current_timestamp() AS _load_ts, 'accounts.csv' AS _source_file
FROM read_files('/Volumes/globaltrader/bronze/landing/accounts.csv', format => 'csv', header => true);

CREATE OR REPLACE TABLE globaltrader.bronze.contacts AS
SELECT *, current_timestamp() AS _load_ts, 'contacts.csv' AS _source_file
FROM read_files('/Volumes/globaltrader/bronze/landing/contacts.csv', format => 'csv', header => true);

CREATE OR REPLACE TABLE globaltrader.bronze.opportunities AS
SELECT *, current_timestamp() AS _load_ts, 'opportunities.csv' AS _source_file
FROM read_files('/Volumes/globaltrader/bronze/landing/opportunities.csv', format => 'csv', header => true);

CREATE OR REPLACE TABLE globaltrader.bronze.products AS
SELECT *, current_timestamp() AS _load_ts, 'products.csv' AS _source_file
FROM read_files('/Volumes/globaltrader/bronze/landing/products.csv', format => 'csv', header => true);

CREATE OR REPLACE TABLE globaltrader.bronze.sales_orders AS
SELECT *, current_timestamp() AS _load_ts, 'sales_orders.csv' AS _source_file
FROM read_files('/Volumes/globaltrader/bronze/landing/sales_orders.csv', format => 'csv', header => true);

-- Sanity check: row counts across all five bronze tables in one shot.
SELECT 'accounts' AS table_name, count(*) AS row_count FROM globaltrader.bronze.accounts
UNION ALL
SELECT 'contacts', count(*) FROM globaltrader.bronze.contacts
UNION ALL
SELECT 'opportunities', count(*) FROM globaltrader.bronze.opportunities
UNION ALL
SELECT 'products', count(*) FROM globaltrader.bronze.products
UNION ALL
SELECT 'sales_orders', count(*) FROM globaltrader.bronze.sales_orders;

-- Left alone on purpose - don't load these here:
--   accounts_batch2_incremental.csv  -> yours to MERGE in Phase 3 (T018)
--   website_events.jsonl             -> yours to ingest in Phase 6 (Auto Loader/DLT)
