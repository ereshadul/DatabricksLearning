"""
grow_data.py
-------------
Optional Python wrapper around grow_data.sql, for two cases the plain SQL
script doesn't cover well:

  1. You want to inflate the table FAST - e.g. run 20 batches back-to-back
     right before a performance-tuning exercise instead of clicking "Run"
     in the SQL editor 20 times.
  2. You want it to run unattended over real wall-clock time (e.g. one
     batch every 10 minutes for the next few hours) to simulate genuinely
     continuous arrival, while you work on something else.

If neither of those matter to you, just use grow_data.sql directly in the
SQL editor - it's simpler and needs no token.

Uses the same DATABRICKS_HOST / DATABRICKS_TOKEN / WAREHOUSE_ID as
load_to_databricks.py.
"""

import time
from pathlib import Path

import requests

# ---- FILL THESE IN -----------------------------------------------------
DATABRICKS_HOST = "https://PASTE_YOUR_WORKSPACE_URL_HERE.cloud.databricks.com"
DATABRICKS_TOKEN = "PASTE_YOUR_TOKEN_HERE"
WAREHOUSE_ID = "PASTE_YOUR_SQL_WAREHOUSE_ID_HERE"
# --------------------------------------------------------------------------

# ---- HOW MUCH AND HOW OFTEN ----------------------------------------------
BATCH_SIZE = 500       # rows added per run
NUM_RUNS = 5           # how many batches to fire this session
SLEEP_SECONDS = 0      # set to e.g. 600 to space runs out over real time
# --------------------------------------------------------------------------

CATALOG = "globaltrader"
TABLE = f"{CATALOG}.bronze.order_activity_log"
HEADERS = {"Authorization": f"Bearer {DATABRICKS_TOKEN}"}

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
  activity_id    STRING,
  account_id     STRING,
  rep            STRING,
  product_id     STRING,
  activity_type  STRING,
  amount_usd     DOUBLE,
  activity_ts    TIMESTAMP,
  _load_ts       TIMESTAMP,
  _source_file   STRING
)
"""

INSERT_BATCH_SQL = f"""
INSERT INTO {TABLE}
  (activity_id, account_id, rep, product_id, activity_type, amount_usd, activity_ts, _load_ts, _source_file)
WITH ref_accounts AS (
  SELECT collect_list(account_id) AS ids FROM {CATALOG}.bronze.accounts
),
ref_products AS (
  SELECT collect_list(product_id) AS ids FROM {CATALOG}.bronze.products
),
ref_reps AS (
  SELECT array('Alex Morgan', 'Emma Schulz', 'Omar Khalid', 'Priya Nair') AS names
),
ref_types AS (
  SELECT array('call', 'email', 'demo_scheduled', 'quote_sent', 'order_placed',
               'order_shipped', 'support_ticket', 'renewal_check_in') AS types
)
SELECT
  concat('ACT-', date_format(current_timestamp(), 'yyyyMMddHHmmss'), '-', lpad(cast(r.id AS string), 6, '0')),
  element_at(ref_accounts.ids, cast(rand() * size(ref_accounts.ids) AS int) + 1),
  element_at(ref_reps.names, cast(rand() * size(ref_reps.names) AS int) + 1),
  element_at(ref_products.ids, cast(rand() * size(ref_products.ids) AS int) + 1),
  element_at(ref_types.types, cast(rand() * size(ref_types.types) AS int) + 1),
  CASE WHEN rand() < 0.4 THEN round(rand() * 90000 + 500, 2) ELSE NULL END,
  current_timestamp() - make_interval(0, 0, 0, 0, 0, 0, cast(rand() * 259200 AS int)),
  current_timestamp(),
  'synthetic_growth_batch'
FROM range(1, {BATCH_SIZE + 1}) AS r(id)
CROSS JOIN ref_accounts
CROSS JOIN ref_products
CROSS JOIN ref_reps
CROSS JOIN ref_types
"""


def run_sql(statement: str):
    resp = requests.post(
        f"{DATABRICKS_HOST}/api/2.0/sql/statements",
        headers=HEADERS,
        json={"warehouse_id": WAREHOUSE_ID, "statement": statement, "wait_timeout": "30s"},
    )
    resp.raise_for_status()
    result = resp.json()
    statement_id = result["statement_id"]
    while result["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(1)
        result = requests.get(
            f"{DATABRICKS_HOST}/api/2.0/sql/statements/{statement_id}", headers=HEADERS
        ).json()
    state = result["status"]["state"]
    if state != "SUCCEEDED":
        raise RuntimeError(f"SQL failed ({state}):\n{statement[:200]}\n-> {result['status']}")
    return result


def row_count():
    result = run_sql(f"SELECT count(*) FROM {TABLE}")
    return result["result"]["data_array"][0][0]


def num_files():
    result = run_sql(f"DESCRIBE DETAIL {TABLE}")
    columns = [c["name"] for c in result["manifest"]["schema"]["columns"]]
    row = result["result"]["data_array"][0]
    return row[columns.index("numFiles")]


def main():
    if "PASTE_YOUR" in DATABRICKS_TOKEN or "PASTE_YOUR" in WAREHOUSE_ID or "PASTE_YOUR" in DATABRICKS_HOST:
        print("Fill in DATABRICKS_HOST, DATABRICKS_TOKEN, and WAREHOUSE_ID at the top of this file first.")
        return

    print(f"Ensuring {TABLE} exists...")
    run_sql(CREATE_TABLE_SQL)

    for i in range(1, NUM_RUNS + 1):
        run_sql(INSERT_BATCH_SQL)
        print(f"  batch {i}/{NUM_RUNS}: +{BATCH_SIZE} rows")
        if i < NUM_RUNS and SLEEP_SECONDS > 0:
            time.sleep(SLEEP_SECONDS)

    print(f"\nDone. {TABLE} now has {row_count()} rows across {num_files()} files.")
    print("That file count is the small-file problem in action - go run OPTIMIZE/ZORDER on it.")


if __name__ == "__main__":
    main()
