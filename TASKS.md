# DatabricksLearning — Task List

GlobalTrader Inc. Lakehouse project. 56 tasks across 9 phases (Phase 0–8), ramping from
first-login basics to production-style orchestration. Every task has a **Do** (what to
actually type/click) and a **Done when** (how you know it worked) — this isn't a list of
topics to read about, it's a list of things to go do.

SQL-first throughout, with two explicit PySpark checkpoints (T020, T041) where you ask
for the code and compare it to the SQL version you already wrote — no separate PySpark
lesson, just two concrete points where it's actually relevant.

Phase 9 (Capstone) and Phase 10 (Interview Prep) are not task lists — see `CAPSTONE.md`
and `INTERVIEW.md`.

Reps: Alex Morgan, Emma Schulz, Omar Khalid, Priya Nair.
Anchor accounts: Meridian Industrial Group, Vantix Aerospace Systems.

---

## Phase 0 — Orientation & Workspace Setup

Get the workspace ready and the data in, so every later phase starts from a working
baseline instead of an empty shell.

**T001. Sign up for Databricks Free Edition.**
Do: Go to the Databricks Free Edition signup page. Sign in with email, Google, or
Microsoft — no credit card or AWS account needed. Wait for the workspace to provision
(usually under a minute).
Done when: You're looking at the Databricks workspace home screen with the left sidebar
visible.

**T002. Tour the workspace.**
Do: Click through each item in the left sidebar once: Notebooks (code/SQL cells, the main
workspace), SQL Editor (one-off SQL queries and dashboards), Catalog (Catalog Explorer —
browse catalogs, schemas, tables, volumes), Workflows (scheduled Jobs and Delta Live
Tables pipelines), Compute (your clusters and SQL warehouses).
Done when: You can describe what each of those five is for, in one sentence, without
looking it up.

**T003. Find your SQL Warehouse and its Warehouse ID.**
Do: Click Compute in the sidebar → SQL Warehouses tab. Free Edition gives you one
serverless warehouse already running. Click into it, open Connection details, and copy
the Warehouse ID.
Done when: You have the Warehouse ID saved somewhere you can paste it from.

**T004. Generate a personal access token.**
Do: Click your name/avatar (top right) → Settings → Developer → Access tokens →
Generate new token. Give it a name and an expiry, then copy the token immediately —
Databricks only shows it once.
Done when: You have your workspace URL, the token, and the Warehouse ID from T003 all in
one place.

**T005. Run the bulk data loader.**
Do: Open `load_to_databricks.py`, paste in `DATABRICKS_HOST` (your workspace URL),
`DATABRICKS_TOKEN` (from T004), and `WAREHOUSE_ID` (from T003). Run
`python load_to_databricks.py`. Skipping Python entirely? Open `bootstrap_bronze.sql`
instead — its header tells you to first upload the 7 files from `/data` into a volume
through the Catalog Explorer UI, then paste the rest of the SQL into the SQL editor and
run it.
Done when: The script prints "Done" with no `FAILED` lines (or, for the SQL version, all
statements ran without error).

**T006. Verify everything landed.**
Do: In Catalog Explorer, open `globaltrader` → `bronze`. You should see 5 tables:
`accounts`, `contacts`, `opportunities`, `products`, `sales_orders`. Open the `landing`
volume inside `bronze` and confirm all 7 files from `/data` are sitting there (including
the two you haven't loaded into tables yet).
Done when: 5 tables + 7 files, and row counts match `DATA_REFERENCE.xlsx` when you
spot-check one or two tables.

## Phase 1 — Bronze Layer: Understand & Practice the Load

The loader already built the real bronze tables. This phase is about understanding
exactly how, and getting the underlying syntax into your own hands on a throwaway copy —
not redoing real work twice.

**T007. Inspect the lineage columns.**
Do: Run `SELECT * FROM globaltrader.bronze.accounts LIMIT 5;` and look at the `_load_ts`
and `_source_file` columns the loader added.
Done when: You can explain what those two columns are for and why a real pipeline needs
them.

**T008. Read the loader's actual SQL.**
Do: Open `load_to_databricks.py` (or `bootstrap_bronze.sql`) and find the
`CREATE OR REPLACE TABLE ... SELECT ... FROM read_files(...)` block. Read it line by
line.
Done when: You can explain what `read_files('path', format => 'csv', header => true)` is
doing, in your own words.

**T009. Manually load a file by hand.**
Do: On a throwaway table (not the real `bronze.accounts`), run:
```sql
CREATE TABLE globaltrader.bronze.accounts_practice
USING CSV
OPTIONS (path '/Volumes/globaltrader/bronze/landing/accounts.csv', header 'true');
```
Then try the same thing with `COPY INTO` instead. Drop `accounts_practice` once you're
done with both.
Done when: You've typed both the `CREATE TABLE ... USING CSV` and `COPY INTO` syntax
yourself at least once, not just read them.

**T010. Test COPY INTO idempotency.**
Do: Re-run the same `COPY INTO` command from T009 a second time against the same
practice table, before dropping it.
Done when: Row count hasn't doubled — explain in a comment why `COPY INTO` tracks which
files it already loaded.

**T011. Check DESCRIBE HISTORY.**
Do: Run `DESCRIBE HISTORY globaltrader.bronze.accounts;` and look at the most recent row.
Done when: You can identify which operation (`CREATE OR REPLACE TABLE AS SELECT`)
created the current version, and roughly when the loader ran.

**T012. Validate row counts.**
Do: Run `SELECT count(*) FROM globaltrader.bronze.<table>;` for all 5 bronze tables.
Done when: Every count matches the row count shown for that file on the Overview sheet
of `DATA_REFERENCE.xlsx`.

## Phase 2 — SQL Fundamentals on Databricks

Standard SQL work, just on Databricks instead of SSMS — this is where your existing
T-SQL instincts transfer almost directly.

**T013. Cross-table SQL.**
Do: Write a query joining `opportunities` to `accounts` to get total opportunity value
by rep, then by region.
Done when: You have at least one query with a JOIN, a GROUP BY, and an ORDER BY
together.

**T014. Build a silver view.**
Do: `CREATE VIEW globaltrader.silver.account_opportunities AS SELECT ... FROM
bronze.accounts a JOIN bronze.opportunities o ON ...` — a view, not a table.
Done when: Querying the view returns joined rows without you having materialized
anything.

**T015. Read a query plan.**
Do: Run `EXPLAIN` in front of one of your T013 queries.
Done when: You can point at the scan, the join, and the aggregation steps in the output
and say which one is doing the most work.

**T016. Build a dashboard.**
Do: In the SQL Editor, save 2-3 of your queries, then use "Add to dashboard" to build a
Databricks SQL Dashboard from them.
Done when: The dashboard renders and updates if you change a query underneath it.

**T017. Schedule a query + alert.**
Do: Pick one query (e.g. total open pipeline value) and schedule it to refresh on an
interval. Add an alert condition, e.g. "pipeline value > $50,000."
Done when: The schedule is active and you've manually triggered the alert once to see
what it looks like.

**T018. SQL Warehouse vs. all-purpose cluster.**
Do: No new query this time — write 3-4 sentences comparing when you'd use each for this
kind of workload (latency, autoscaling, cost model).
Done when: You could explain the difference to someone who's never used Databricks.

## Phase 3 — Delta Lake Core Concepts

This is the part that's actually different from a regular SQL database — Delta Lake's
transaction log is what makes everything else in this project possible.

**T019. MERGE INTO.**
Do:
```sql
MERGE INTO globaltrader.bronze.accounts AS target
USING (
  SELECT *, current_timestamp() AS _load_ts,
         'accounts_batch2_incremental.csv' AS _source_file
  FROM read_files('/Volumes/globaltrader/bronze/landing/accounts_batch2_incremental.csv',
                   format => 'csv', header => true)
) AS source
ON target.account_id = source.account_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```
Done when: `bronze.accounts` row count goes from 20 to 25 (the 5 new accounts in the
incremental file).

**T020. (PySpark) DeltaTable.merge() equivalent.**
Do: Ask for the PySpark version of T019 using
`DeltaTable.forName(spark, "globaltrader.bronze.accounts").merge(...)`. Run it against a
fresh copy of the table, not the one you just merged into.
Done when: You've run both versions and can say which one you'd rather maintain.

**T021. Time travel with VERSION AS OF.**
Do: `SELECT * FROM globaltrader.bronze.accounts VERSION AS OF <version before your
merge>;` (find the version number from T011's `DESCRIBE HISTORY`).
Done when: You see 20 accounts in the old version and 25 in the current one.

**T022. RESTORE TABLE.**
Do: `RESTORE TABLE globaltrader.bronze.accounts TO VERSION AS OF <pre-merge version>;`
then redo the T019 merge.
Done when: You've actually rolled a table back and replayed a change, not just read
about how it works.

> Tip: T023's before/after won't look dramatic on `bronze.opportunities` since it's
> small and clean. Run `grow_data.sql` a few times first and repeat T023 against
> `bronze.order_activity_log` too, where fragmentation is actually visible.

**T023. OPTIMIZE ... ZORDER BY.**
Do: `OPTIMIZE globaltrader.bronze.opportunities ZORDER BY (owner_rep, stage);` Check
`DESCRIBE DETAIL globaltrader.bronze.opportunities;` before and after for `numFiles`.
Done when: You can read the file-count change and explain what Z-ORDER did to get
there.

**T024. VACUUM.**
Do: On a test table only — never on `bronze.opportunities` if you want T023's history
intact — run `VACUUM <test_table> RETAIN 168 HOURS;`
Done when: You can explain in your own words what happens if you `VACUUM` with too short
a retention window while someone's still time-traveling on that table.

**T025. Schema evolution.**
Do: Add a new column to a copy of the incremental CSV, then merge it in using schema
evolution (e.g. `mergeSchema` or `WITH SCHEMA EVOLUTION`, depending on which load path
you use — ask for the current exact syntax if it's changed since this was written).
Done when: The new column shows up in the table without you manually running
`ALTER TABLE`.

**T026. ACID guarantees note.**
Do: Write 3-4 sentences explaining what ACID means here, using a concrete scenario: two
processes writing to `bronze.accounts` at the same time.
Done when: Your explanation mentions the transaction log specifically, not just "it's
safe."

## Phase 4 — Silver Layer: Cleaning & Modeling

Bronze is raw. Silver is the first place data actually gets trustworthy — dedup,
standardize, and start modeling relationships properly.

**T027. Dedupe accounts.**
Do: Build `silver.accounts` using
`ROW_NUMBER() OVER (PARTITION BY account_name, region ORDER BY created_date DESC)` to
keep one row per account/region combo.
Done when: `silver.accounts` row count is less than or equal to `bronze.accounts`.

**T028. Standardize contacts.**
Do: Build `silver.contacts` with phone numbers normalized to one format (e.g.
`(XXX) XXX-XXXX`) and emails lowercased.
Done when: A `SELECT DISTINCT` check on the phone format pattern returns exactly one
shape.

**T029. Build a Type-2 SCD.**
Do: Add `effective_date`, `end_date`, `is_current` to `silver.accounts` and use `MERGE`
to expire old rows and insert new ones when an account's attributes change (use the
incremental batch to simulate a change).
Done when: Querying `WHERE is_current = true` returns exactly one row per account, and
querying without that filter shows history.

**T030. Clean opportunity stages.**
Do: Build `silver.opportunities` with a normalized stage column (collapse any
inconsistent casing/spelling) and a calculated `days_in_pipeline` column
(`datediff(close_date, created_date)`).
Done when: `days_in_pipeline` has no negative values.

**T031. Opportunity-to-order conversion.**
Do: Join `silver.opportunities` to `bronze.sales_orders` to compute conversion rate by
rep — closed-won opportunities that actually became an order, divided by total
closed-won.
Done when: You have one number per rep, not just an overall average.

**T032. Data quality checks.**
Do: Add at least one `CHECK` constraint (e.g. `amount_usd >= 0`) and one validation
query (e.g. no `account_id` in opportunities that doesn't exist in accounts).
Done when: You've documented, in a comment, what real-world bad data each check would
actually catch.

## Phase 5 — Gold Layer: Analytics-Ready

This is the layer a dashboard or an executive actually touches — model it like you mean
it.

**T033. Build the fact table.**
Do: `gold.fact_sales` joining `silver` sales/opportunity data, with foreign keys to the
dimension tables you're about to build.
Done when: Every row has a non-null account_id, product_id, and rep.

**T034. Build dimension tables.**
Do: `gold.dim_account`, `gold.dim_rep`, `gold.dim_product`, and `gold.dim_date` — a real
date dimension, one row per day in your data's range, with year/month/quarter columns.
Done when: `gold.dim_date` has no gaps for the date range your data covers.

**T035. Rep-performance view.**
Do: Build a view on top of the star schema showing pipeline value, win rate, and closed
revenue per rep.
Done when: The numbers in this view match what you'd get joining the raw bronze tables
yourself (sanity check it).

**T036. Gold-layer dashboard.**
Do: Build a Databricks SQL Dashboard (or an AI/BI Genie space) for "exec readout" style
reporting on the gold layer specifically — not bronze.
Done when: A non-technical person could open it and understand the headline number in
10 seconds.

**T037. Materialized view.**
Do: Pick your heaviest aggregation (probably the rep-performance numbers) and rebuild it
as a Materialized View instead of a plain view.
Done when: You can explain when it refreshes and how that's different from a regular
view recalculating on every query.

## Phase 6 — Streaming & Auto Loader

Everything so far has been batch. This is the one part of the project that's genuinely
about data arriving continuously, not just sitting in a file.

**T038. Confirm the events file is ready.**
Do: `website_events.jsonl` was already uploaded to the volume by the loader in T005 —
you don't need to re-upload it. Run
`SELECT * FROM read_files('/Volumes/globaltrader/bronze/landing/website_events.jsonl', format => 'json') LIMIT 5;`
to preview its structure.
Done when: You can name all 6 fields in an event row (`event_id`, `account_id`,
`session_id`, `event_type`, `page`, `event_ts`) without looking at the file again.

**T039. Auto Loader ingestion.**
Do: Set up `cloudFiles` to incrementally ingest from the volume path into
`bronze.website_events`, using a checkpoint location under the same volume.
Done when: The table has 160 rows after the first run, and a second run with no new
files adds zero more.

**T040. Delta Live Tables pipeline (SQL).**
Do: Create a DLT/Lakeflow pipeline using the `CREATE STREAMING TABLE` SQL syntax for
bronze → silver on the events data — no Python required for this version. (Ask for the
exact current syntax if it's drifted since this was written; DLT's SQL surface changes
fairly often.)
Done when: The pipeline runs end to end in the pipeline UI and shows green on both
layers.

**T041. (PySpark) Structured Streaming equivalent.**
Do: Ask for the PySpark `readStream`/`writeStream` version of T039/T040 and run it side
by side with the DLT version.
Done when: You can point at which lines are pure boilerplate in the PySpark version that
DLT handled for you automatically.

**T042. Checkpoint & exactly-once.**
Do: Find the checkpoint folder Auto Loader created and look at what's inside it.
Done when: You can explain, in your own words, what "exactly-once" actually means here
and what would happen if you deleted the checkpoint and reran.

**T043. DLT vs. hand-written streaming — comparison.**
Do: Write 3-4 sentences: when would you reach for DLT's declarative SQL vs. your T041
PySpark job?
Done when: Your answer mentions at least one concrete scenario where each wins (e.g. DLT
for standard bronze/silver patterns, PySpark for custom logic DLT doesn't support).

**T044. Trigger and inspect a run.**
Do: Manually trigger the pipeline once more and open the event metrics / data quality
expectations panel.
Done when: You can read the rows-processed and rows-dropped numbers and explain what
dropped (if anything).

## Phase 7 — Governance, Security & Unity Catalog

This is the phase that separates "I built a pipeline" from "I built a pipeline I'd
trust with someone else's data."

**T045. Row filter.**
Do: Write a SQL function that returns true only when `current_user()` matches a
simulated regional-analyst mapping, then
`ALTER TABLE gold.dim_account SET ROW FILTER <function_name> ON (region);`
Done when: Querying as yourself (admin) shows all rows; you can demonstrate (via a
second simulated user/role) that a restricted role sees fewer.

**T046. Column masking.**
Do: Write a masking function for `silver.contacts.email`/`phone` (e.g. show only the
domain, or redact most digits) and apply it with
`ALTER TABLE silver.contacts ALTER COLUMN email SET MASK <function_name>;`
Done when: A privileged role sees the real value; a restricted role sees the masked one,
on the exact same query.

**T047. Grant/revoke permissions.**
Do: Create a simulated "analyst" group reference and
`GRANT SELECT ON CATALOG globaltrader TO <group>;`, then `REVOKE` it on one specific
table to show table-level overrides work.
Done when: You've run both a GRANT and a REVOKE, not just one.

**T048. Data lineage graph.**
Do: In Catalog Explorer, open `gold.fact_sales` → Lineage tab.
Done when: You can trace the graph all the way back to the source CSV files.

**T049. Audit log query.**
Do: Query the Unity Catalog system tables (`system.access.audit`) for access events on
your tables in the last 7 days.
Done when: You can see at least your own queries from earlier tasks show up.

**T050. Tag sensitive columns.**
Do: Tag `silver.contacts.email`/`phone` as PII and a financial column on
`gold.fact_sales` as financial data, using Unity Catalog tags.
Done when: The tags are visible in Catalog Explorer's column details.

## Phase 8 — Orchestration & Monitoring

Everything you built so far still needs something to actually run it on a schedule,
retry it when it fails, and tell you when it's broken.

**T051. Build a Workflow.**
Do: Create a Databricks Job chaining your bronze → silver → gold build steps as ordered
tasks.

> Tip: for the most realistic version of "this table won't stop growing," add
> `grow_data.sql` as one more task in this same Job on a schedule (e.g. every 15
> minutes) instead of running it by hand — that's an actual continuously-arriving
> table, not a simulation of one.

Done when: A manual run of the Job completes all tasks in order, green end to end.

**T052. Dependencies & retry policy.**
Do: Add explicit task dependencies (silver tasks depend on bronze completing) and a
retry policy (e.g. 2 retries, 5 minute backoff) on at least one task.
Done when: You can point at the dependency graph in the UI and explain the retry setting
without re-reading the docs.

**T053. Failure notification.**
Do: Add an email or webhook notification that fires on task failure.
Done when: You've actually triggered a failure (break one query on purpose) and
received the notification.

**T054. Data-quality gate.**
Do: Add a task that runs a validation query (e.g. no negative amounts, no orphaned
account_ids) and fails the Job if it finds bad rows.
Done when: You've proven it works by feeding it deliberately bad data once and watching
the Job stop.

**T055. Review job history & cost.**
Do: Open Job run history, look at cluster/serverless utilization and cost-per-run for
your last few runs.
Done when: You can say which task in the Job is the most expensive and why.

**T056. Write a runbook.**
Do: One page: the Job's SLA, the most likely way it breaks, and the first three things
you'd check if paged about it.
Done when: A stranger could follow your runbook and triage the same way you would.
