-- grow_data.sql
-- ----------------
-- Simulates the thing every real project eventually deals with: a table that
-- just keeps getting bigger. Run this block again any time you want to add
-- another "day" of business activity. Each run appends a new random batch -
-- it never overwrites, so the table grows a little more fragmented every
-- time, exactly like a real un-tuned operational table would.
--
-- Run this AFTER load_to_databricks.py / bootstrap_bronze.sql (it reads the
-- account/product lists from those tables to keep things relational).
--
-- HOW TO USE IT:
--   - Run it once to create the table and add the first batch.
--   - Run it again (and again) whenever you want more rows - paste the whole
--     block into the SQL editor and hit run. No setup, no token, no Python.
--   - Change the 501 below to a bigger number for a bigger batch (e.g. 5001
--     for 5,000 rows in one shot, if you want to inflate it fast before a
--     performance-tuning exercise).
--
-- WHY THIS TABLE SPECIFICALLY: it's deliberately separate from the curated
-- GlobalTrader bronze tables (accounts/contacts/opportunities/products/
-- sales_orders), so growing it never breaks the row-count checks or join
-- logic those tables are used for elsewhere in TASKS.md. This one is just
-- for "now go tame a table that won't stop growing."

CREATE TABLE IF NOT EXISTS globaltrader.bronze.order_activity_log (
  activity_id    STRING,
  account_id     STRING,
  rep            STRING,
  product_id     STRING,
  activity_type  STRING,
  amount_usd     DOUBLE,
  activity_ts    TIMESTAMP,
  _load_ts       TIMESTAMP,
  _source_file   STRING
);

INSERT INTO globaltrader.bronze.order_activity_log
  (activity_id, account_id, rep, product_id, activity_type, amount_usd, activity_ts, _load_ts, _source_file)
WITH ref_accounts AS (
  SELECT collect_list(account_id) AS ids FROM globaltrader.bronze.accounts
),
ref_products AS (
  SELECT collect_list(product_id) AS ids FROM globaltrader.bronze.products
),
ref_reps AS (
  SELECT array('Alex Morgan', 'Emma Schulz', 'Omar Khalid', 'Priya Nair') AS names
),
ref_types AS (
  SELECT array('call', 'email', 'demo_scheduled', 'quote_sent', 'order_placed',
               'order_shipped', 'support_ticket', 'renewal_check_in') AS types
)
SELECT
  concat('ACT-', date_format(current_timestamp(), 'yyyyMMddHHmmss'), '-', lpad(cast(r.id AS string), 6, '0')) AS activity_id,
  element_at(ref_accounts.ids, cast(rand() * size(ref_accounts.ids) AS int) + 1) AS account_id,
  element_at(ref_reps.names, cast(rand() * size(ref_reps.names) AS int) + 1) AS rep,
  element_at(ref_products.ids, cast(rand() * size(ref_products.ids) AS int) + 1) AS product_id,
  element_at(ref_types.types, cast(rand() * size(ref_types.types) AS int) + 1) AS activity_type,
  CASE WHEN rand() < 0.4 THEN round(rand() * 90000 + 500, 2) ELSE NULL END AS amount_usd,
  current_timestamp() - make_interval(0, 0, 0, 0, 0, 0, cast(rand() * 259200 AS int)) AS activity_ts,
  current_timestamp() AS _load_ts,
  'synthetic_growth_batch' AS _source_file
FROM range(1, 501) AS r(id)
CROSS JOIN ref_accounts
CROSS JOIN ref_products
CROSS JOIN ref_reps
CROSS JOIN ref_types;

-- Quick check after running - two separate statements (DESCRIBE DETAIL
-- doesn't reliably nest as a subquery). Watch numFiles climb across
-- repeated runs until you OPTIMIZE it.
SELECT count(*) AS row_count FROM globaltrader.bronze.order_activity_log;

DESCRIBE DETAIL globaltrader.bronze.order_activity_log;
-- ^ look at the numFiles column in the result
