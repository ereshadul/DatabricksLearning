# DatabricksLearning

Self-directed Databricks + Delta Lake learning project, built around the same fictional
company used in the D365CRM and SnowflakesLearning projects: **GlobalTrader Inc.**

This keeps the data familiar (same accounts, same reps) so the new thing to learn is
Databricks itself — not a new business scenario on top of it.

## Why SQL-first

Databricks gets sold as a Python/PySpark platform, but most of the actual differentiators —
Delta Lake, Unity Catalog, Delta Live Tables, SQL Warehouses, dashboards — work fully in SQL.
This project uses SQL everywhere it can. PySpark isn't a dedicated phase: wherever a task
could use it, just ask for the PySpark equivalent at that point and pick it up as you go,
rather than front-loading a syntax lesson before you have a reason to use it.

## Structure

```
DatabricksLearning/
├── README.md
├── TASKS.md                # 56 tasks, Phases 0-8, slow start -> advanced, each with Do/Done-when detail
├── CAPSTONE.md              # Phase 9 - real build & demo, not a checklist
├── INTERVIEW.md             # Phase 10 - mock technical round, hands-on
├── DATA_REFERENCE.xlsx      # every data file, in Excel, so you can see what you uploaded
├── setup_repo.py            # one-time script: pushes files + opens GitHub issues
├── load_to_databricks.py    # one-time script: bulk-loads data INTO your Databricks workspace
├── bootstrap_bronze.sql     # pure-SQL alternative to load_to_databricks.py
├── grow_data.sql            # run repeatedly - keeps adding random rows to simulate a growing table
├── grow_data.py             # optional wrapper to fire grow_data.sql fast or on a timer
└── data/
    ├── accounts.csv
    ├── accounts_batch2_incremental.csv   # for Auto Loader / COPY INTO / MERGE practice
    ├── contacts.csv
    ├── opportunities.csv
    ├── products.csv
    ├── sales_orders.csv
    └── website_events.jsonl              # for the streaming / Auto Loader phase
```

## Starting with data already in place

`load_to_databricks.py` (or `bootstrap_bronze.sql` if you'd rather skip Python
entirely) pushes the catalog, schemas, volume, and all 7 data files straight
into your Databricks workspace, and loads the 5 core CSVs into real bronze
Delta tables. Run it before Phase 0 and you open your workspace to a
populated, 5-table relational scenario instead of an empty one.

It deliberately leaves two things as files only, not tables, so the related
tasks are still real exercises: `accounts_batch2_incremental.csv` (Phase 3,
T019 - MERGE INTO) and `website_events.jsonl` (Phase 6 - Auto Loader/DLT).

## Simulating a table that keeps growing

Real projects always have at least one table that just won't stop getting
bigger and eventually becomes a problem. `grow_data.sql` recreates that: run
it again any time and it appends another random batch of rows to
`bronze.order_activity_log` (a separate table, created the first time you run
it - it doesn't touch your curated GlobalTrader tables). No setup needed,
just paste it into the SQL editor and run it.

Run it a handful of times before Phase 3's `OPTIMIZE`/`ZORDER` task and
you'll have an actual small-file problem to diagnose and fix instead of a
clean table that doesn't show much difference either way. `grow_data.py` is
the same thing as an external script, useful if you want to fire off many
batches at once or let it run on a timer in the background.

For the most realistic version of this, Phase 8 has a tip about scheduling
`grow_data.sql` as a recurring task inside your own Databricks Job - at that
point it's not a simulation, it's an actual continuously-arriving table.

## Seeing what you actually uploaded

`DATA_REFERENCE.xlsx` has every data file as its own sheet, plus an Overview
sheet mapping each file to the table it becomes and the phase/task that uses
it. Open it any time you want to see the raw rows behind a query result
without going back into Databricks.

## Free, already-there datasets if you want more scale

Every Databricks workspace, including Free Edition, ships with a `samples`
catalog - zero setup, query it immediately:

- `samples.tpch.*` - the TPC-H benchmark: customers, orders, lineitem,
  supplier, part, nation, region. A real multi-table relational schema, useful
  for Phase 3's `OPTIMIZE`/`ZORDER` work where having more rows actually shows
  a difference.
- `samples.tpcds_sf1.*` - TPC-DS at scale factor 1: dozens of fact/dimension
  tables, classic star-schema shape, good for Phase 5 (Gold layer) practice
  beyond GlobalTrader's small dimension tables.
- `samples.nyctaxi.trips` - simpler single-table dataset, fine for a quick
  one-off query.

Try `SELECT * FROM samples.tpch.orders LIMIT 10;` in the SQL editor any time -
no loading required.

## Phases at a glance

| Phase | Focus | Tasks |
|---|---|---|
| 0 | Workspace setup, credentials, run the bulk loader | T001–T006 |
| 1 | Bronze layer: understand & practice the load | T007–T012 |
| 2 | SQL fundamentals on Databricks | T013–T018 |
| 3 | Delta Lake core (MERGE, time travel, OPTIMIZE) | T019–T026 |
| 4 | Silver layer: cleaning & modeling | T027–T032 |
| 5 | Gold layer: analytics-ready | T033–T037 |
| 6 | Streaming & Auto Loader (DLT, SQL-first) | T038–T044 |
| 7 | Governance & Unity Catalog security | T045–T050 |
| 8 | Orchestration & monitoring | T051–T056 |
| 9 | **Capstone — build & demo** (see `CAPSTONE.md`) | not task-tracked |
| 10 | **Interview prep — technical Q&A, hands-on** (see `INTERVIEW.md`) | not task-tracked |

PySpark isn't a separate phase, but it isn't skipped either — T020 (Phase 3) and
T041 (Phase 6) are explicit checkpoints where you ask for the PySpark version of a
task you already did in SQL and compare the two. That's the whole PySpark curriculum:
two real comparisons, not a syntax unit.

## Setup

**GitHub tracking (optional, for the task issues):**

1. Create the repo on GitHub: `github.com/new` → name it `DatabricksLearning` → Create.
2. Put this whole folder's contents in it locally.
3. Open `setup_repo.py`, paste your GitHub personal access token and username at the top.
4. Run: `python setup_repo.py`

This uploads the README, `TASKS.md`, `CAPSTONE.md`, `INTERVIEW.md`, `DATA_REFERENCE.xlsx`,
the loader scripts, `grow_data.sql`/`.py`, and the `data/` files. It creates one label per
phase and opens one GitHub Issue per task (T001–T056), with the Do/Done-when detail as the
issue body. Phase 9 and Phase 10 each get a
single pinned issue with their full brief as the body — track your own checklist inside it.

**Databricks workspace (where you'll actually do the work):**

Start at T001 in `TASKS.md` — Phase 0 walks you through Free Edition signup, finding
your warehouse ID, generating a token, and running the bulk loader, in that order, with
exact steps for each. By T006 your bronze layer is already populated and verified.

Whenever you want, run `grow_data.sql` in the SQL editor a few times — it's independent
of the rest of the setup and just adds more rows to `bronze.order_activity_log`.
