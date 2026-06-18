"""
load_to_databricks.py
----------------------
Run this once against your Databricks Free Edition workspace and it does the
following, so you open the workspace to an already-populated, multi-table
scenario instead of an empty one:

  1. Creates the `globaltrader` catalog and bronze/silver/gold schemas.
  2. Creates a Unity Catalog Volume and uploads ALL files from /data into it
     (including the files you're meant to load yourself later - see below).
  3. Loads the 5 core CSVs into real bronze Delta tables, with lineage
     columns (_load_ts, _source_file) already on them.

On purpose, this script does NOT:
  - Merge accounts_batch2_incremental.csv into bronze.accounts - that's
    Phase 3 / T018 (MERGE INTO), the file just sits in the volume ready.
  - Ingest website_events.jsonl into a table - that's Phase 6 (Auto Loader /
    Delta Live Tables), the file just sits in the volume ready.

So Phase 0/1 effectively run themselves, and you land straight in a
populated 5-table relational scenario for Phase 2 onward - while the
streaming and incremental-merge exercises are still untouched for you to do.

WHAT YOU NEED FIRST (all from inside your Databricks workspace):
  - DATABRICKS_HOST: your workspace URL, e.g. https://dbc-xxxx.cloud.databricks.com
  - DATABRICKS_TOKEN: Settings (your name, top right) -> Developer ->
    Access tokens -> Generate new token
  - WAREHOUSE_ID: SQL Warehouses (left sidebar) -> click your warehouse ->
    Connection details tab -> Warehouse ID

If token generation isn't available on your account (some Free Edition
accounts restrict this), use bootstrap_bronze.sql instead - same end
result, no Python, you just upload the files through the UI first.

Run:  pip install requests --break-system-packages   (if not already installed)
      python load_to_databricks.py
"""

import time
from pathlib import Path

import requests

# ---- FILL THESE IN -----------------------------------------------------
DATABRICKS_HOST = "https://PASTE_YOUR_WORKSPACE_URL_HERE.cloud.databricks.com"
DATABRICKS_TOKEN = "PASTE_YOUR_TOKEN_HERE"
WAREHOUSE_ID = "PASTE_YOUR_SQL_WAREHOUSE_ID_HERE"
# --------------------------------------------------------------------------

CATALOG = "globaltrader"
VOLUME_PATH = f"/Volumes/{CATALOG}/bronze/landing"
CORE_TABLES = ["accounts", "contacts", "opportunities", "products", "sales_orders"]

HEADERS = {"Authorization": f"Bearer {DATABRICKS_TOKEN}"}
DATA_DIR = Path(__file__).parent / "data"


def run_sql(statement: str):
    """Run one SQL statement on the warehouse and wait for it to finish."""
    resp = requests.post(
        f"{DATABRICKS_HOST}/api/2.0/sql/statements",
        headers=HEADERS,
        json={"warehouse_id": WAREHOUSE_ID, "statement": statement, "wait_timeout": "30s"},
    )
    resp.raise_for_status()
    result = resp.json()
    statement_id = result["statement_id"]

    # Poll until the statement is done (covers the rare case it didn't
    # finish within the initial wait_timeout window).
    while result["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(1)
        result = requests.get(
            f"{DATABRICKS_HOST}/api/2.0/sql/statements/{statement_id}", headers=HEADERS
        ).json()

    state = result["status"]["state"]
    if state != "SUCCEEDED":
        raise RuntimeError(f"SQL failed ({state}):\n{statement}\n-> {result['status']}")
    return result


def upload_file(local_path: Path, volume_path: str):
    """Push one local file into a Unity Catalog Volume via the Files API."""
    data = local_path.read_bytes()
    resp = requests.put(
        f"{DATABRICKS_HOST}/api/2.0/fs/files{volume_path}?overwrite=true",
        headers={**HEADERS, "Content-Type": "application/octet-stream"},
        data=data,
    )
    if resp.status_code in (200, 204):
        print(f"  uploaded {volume_path}")
    else:
        print(f"  FAILED   {volume_path}: {resp.status_code} {resp.text[:200]}")


def main():
    if "PASTE_YOUR" in DATABRICKS_TOKEN or "PASTE_YOUR" in WAREHOUSE_ID or "PASTE_YOUR" in DATABRICKS_HOST:
        print("Fill in DATABRICKS_HOST, DATABRICKS_TOKEN, and WAREHOUSE_ID at the top of this file first.")
        return

    print("Creating catalog, schemas, and volume...")
    run_sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
    run_sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.bronze")
    run_sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.silver")
    run_sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.gold")
    run_sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.bronze.landing")

    print("\nUploading all data files into the volume...")
    for f in sorted(DATA_DIR.glob("*")):
        upload_file(f, f"{VOLUME_PATH}/{f.name}")

    print("\nLoading core bronze tables...")
    for t in CORE_TABLES:
        run_sql(f"""
            CREATE OR REPLACE TABLE {CATALOG}.bronze.{t} AS
            SELECT *,
                   current_timestamp() AS _load_ts,
                   '{t}.csv' AS _source_file
            FROM read_files('{VOLUME_PATH}/{t}.csv', format => 'csv', header => true)
        """)
        print(f"  loaded bronze.{t}")

    print("\nDone. Bronze layer is populated and ready to query in Phase 2.")
    print("Left alone on purpose, as files in the volume only:")
    print("  - accounts_batch2_incremental.csv  -> yours to MERGE in Phase 3 (T018)")
    print("  - website_events.jsonl             -> yours to ingest in Phase 6 (Auto Loader/DLT)")


if __name__ == "__main__":
    main()
