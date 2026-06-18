# Phase 10 — Interview Prep: Technical Q&A, Hands-On

Like CAPSTONE.md, this isn't a task checklist - it's a mock technical round. Each
question is something a real interviewer would actually ask. For every one, do the
hands-on part against your own GlobalTrader workspace before you write or say the
answer - don't answer from memory of a blog post. If you can't do the hands-on part
cleanly, that's the thing to go fix, not the question to skip.

Do this after Phase 8 (Orchestration) at minimum - several questions assume your
Phase 7 governance and Phase 8 orchestration work already exists to point at. The
performance questions assume you've run `grow_data.sql` a few times first so there's
an actual fragmentation problem to find and fix, not a hypothetical one.

---

## SQL Fundamentals & Indexing

**Q1. "Walk me through how you'd index this table for faster lookups."**
Hands-on: Query `bronze.opportunities` filtered by `owner_rep` before and after
running `OPTIMIZE ... ZORDER BY (owner_rep, stage)`. Pull the query profile both
times and compare files/bytes scanned. Then explain out loud: Delta Lake has no
traditional B-tree index - what replaces it (file-level min/max statistics, Z-ORDER
data co-location, liquid clustering, bloom filter indexes for high-cardinality
point lookups).

**Q2. "What's the difference between a clustered and non-clustered index, and how
does that map to a lakehouse?"**
Hands-on: none required - verbal only. Draw the parallel explicitly: clustered index
≈ physical row order ≈ Z-ORDER/liquid clustering co-locating related rows in the
same files. Non-clustered index doesn't really have a Delta equivalent - the closest
analog is a bloom filter index on one column.

**Q3. "This query is slow. How do you find out why?"**
Hands-on: Take one of your gold-layer dashboard queries, run `EXPLAIN`, and name the
most expensive operator. Then open the query profile UI and check bytes/files
scanned vs. pruned.

**Q4. "When would adding more indexing actually make things worse?"**
Hands-on: none required. Talk through write amplification - every traditional index
has to be maintained on every write. Name the Delta equivalent tradeoff: `OPTIMIZE`/
`ZORDER` cost vs. read benefit, and why you don't run it after every single insert.

## Delta Lake & Lakehouse Internals

**Q5. "What does ACID actually mean for a table that's really just files in cloud
storage?"**
Hands-on: Open `DESCRIBE HISTORY` on `bronze.accounts`, point at two different
versions, and explain what the transaction log (`_delta_log`) guarantees that plain
Parquet files sitting in a folder wouldn't.

**Q6. "Someone wrote bad data into a table at 2pm. Walk me through fixing it without
taking the table offline."**
Hands-on: Actually do it on a test table - `VERSION AS OF` to inspect the prior
state, then `RESTORE TABLE` to roll back. Narrate the exact commands as you run them.

**Q7. "Explain the medallion architecture to a non-technical stakeholder in two
sentences."**
Hands-on: none - pure communication test. Use your own bronze/silver/gold layers as
the concrete example, not a generic textbook answer.

**Q8. "What's the small-file problem, and why does it happen?"**
Hands-on: Run `grow_data.sql` a few times without optimizing, then run
`DESCRIBE DETAIL` on `bronze.order_activity_log` and read `numFiles`. Run `OPTIMIZE`
and check it again.

## Performance & Scale

**Q9. "This table used to be fast and now it's slow. What do you check first?"**
Hands-on: Use `bronze.order_activity_log` after several `grow_data.sql` runs as the
live example. Check file count, whether `OPTIMIZE` has run recently, and whether
your query is actually getting partition/file pruning at all.

**Q10. "When do you partition a table vs. just relying on Z-ORDER or liquid
clustering?"**
Hands-on: Compare querying `order_activity_log` filtered by a date range with and
without a date-based partition column. Be ready to explain the failure mode of
over-partitioning (too many tiny partitions) as well as under-partitioning.

**Q11. "What's a broadcast join, and when does Spark pick one automatically?"**
Hands-on: `EXPLAIN` a join between `gold.dim_product` (small) and `gold.fact_sales`
(larger) and find the broadcast operator in the plan.

**Q12. "A job ran fine for months and suddenly started timing out. What's your
triage order?"**
Hands-on: Walk through your own capstone's deliberately-broken scenario as the
worked example - what you checked first, second, third.

## Governance & Security

**Q13. "How do you make sure a regional sales rep only sees their own region's
data, without hand-writing that filter into every query?"**
Hands-on: Re-run the row filter from T045 and actually show it blocking rows for a
different simulated role - don't just describe it.

**Q14. "What's the difference between row-level security and column masking, and
when do you need both?"**
Hands-on: Show your T045 row filter and T046 column mask side by side on the same
table.

**Q15. "How do you prove, after the fact, who accessed a sensitive table and when?"**
Hands-on: Re-run your T049 Unity Catalog audit log query and read the result with
fresh eyes, as if a compliance officer asked you cold.

## Orchestration & Incident Response

**Q16. "Walk me through what happens, end to end, when your nightly pipeline fails
at 3am."**
Hands-on: Reference your Phase 8 job's retry policy and failure notification.
Narrate it like you're actually the one who got paged.

**Q17. "How do you stop one bad batch of data from silently corrupting everything
downstream?"**
Hands-on: Point at your T054 data-quality gate task and explain what specifically
it would have caught.

**Q18. "You need to add one more table to the pipeline tomorrow with zero
downtime. How?"**
Hands-on: none required - discuss schema evolution, backward compatibility, and how
Unity Catalog protects existing consumers while you add something new.

## Capstone Defense & Behavioral

**Q19. "Walk me through the hardest part of the project you just built."**
Hands-on: Use your own `CAPSTONE_WRITEUP.md` as the script - if it doesn't already
answer this convincingly, that's worth fixing before an actual interview does.

**Q20. "What would you do differently if this had to handle 100x the data?"**
Hands-on: Actually inflate `order_activity_log` with several big `grow_data.sql`
batches and see where it starts to strain, then answer from what you observed
instead of guessing.
