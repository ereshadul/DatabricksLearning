# Phase 9 — Capstone: Build & Demo

This phase is not a task checklist. It's a real, end-to-end build you complete and demo
once Phases 0–8 are done. Treat it as the thing you'd actually walk an interviewer through.

## The brief

GlobalTrader Inc.'s leadership wants a single Lakehouse view of sales performance that
combines CRM data (accounts, contacts, opportunities), order data, and website activity —
refreshed automatically, governed properly, and fast enough to put in front of execs.

You are the data engineer who owns it end to end.

## Requirements

1. **Pipeline.** A working Bronze → Silver → Gold pipeline, orchestrated as a Databricks
   Workflow, that runs on a schedule (or on file arrival) with no manual steps.
2. **Incremental + streaming.** At least one source loads incrementally (Auto Loader or
   `COPY INTO`) and the website events feed runs through your DLT/streaming pipeline from
   Phase 6 — not a one-time batch load.
3. **A real question, answered.** Pick one business question leadership actually cares about
   (e.g. "which accounts are browsing the site but have no open opportunity?" or "which reps'
   pipeline is aging out fastest?") and build the gold-layer table/view that answers it.
4. **Governance.** Row filters or column masking from Phase 7 must be live on at least one
   gold table, not just demoed in isolation.
5. **Dashboard.** A Databricks SQL Dashboard (or AI/BI Genie space) that someone non-technical
   could open and understand in under a minute.
6. **Resilience.** Deliberately break something — drop a bad file into the incoming folder,
   or break a schema — and show the pipeline catching it (quality gate, job failure alert,
   or DLT expectation) rather than silently corrupting downstream tables.

## Deliverables

- The pipeline itself, live in your workspace.
- A short `CAPSTONE_WRITEUP.md` (half a page is fine): what you built, the one business
  question you answered, and the one failure you intentionally triggered and how the
  pipeline responded.
- A 5–8 minute demo — screen recording or live walkthrough — covering: data arriving →
  pipeline running → dashboard updating → the deliberate failure → recovery.

## Suggested demo flow

1. Show the Workflow graph (30 sec) — "here's the whole pipeline."
2. Drop the incremental file in, trigger the run, show it landing in Bronze (1 min).
3. Show one Silver transformation that matters (e.g. the SCD2 or the dedupe) (1 min).
4. Open the dashboard, answer the business question live (1–2 min).
5. Break something on purpose, show the catch (1–2 min).
6. One sentence on what you'd do differently at 10x the data volume (30 sec).

## What "done" looks like

If you can run this demo cold, for a stranger, without narrating "imagine if this worked" —
you're done. If you're explaining around a gap, that gap is your next task, not a footnote
in the writeup.
