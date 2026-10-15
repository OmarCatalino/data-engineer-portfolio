-- =============================================================
-- Phase 1 review on a real production-style database (2026-10-15)
-- Read-only practice against a live Postgres (contacts / import_batches /
-- header_maps tables). Queries only — no business data is stored here.
-- =============================================================


-- -------------------------------------------------------------
-- Ex 1 — count(*) vs count(col): rows vs non-NULL values
-- Coverage of a column per category. 100.0 (not 100) forces decimal
-- division; integer / integer truncates in Postgres.
-- -------------------------------------------------------------
SELECT
    source,
    count(*)                                   AS contacts,
    count(email)                               AS with_email,
    round(100.0 * count(email) / count(*), 1)  AS pct_with_email
FROM contacts
GROUP BY source
ORDER BY contacts DESC;


-- -------------------------------------------------------------
-- Ex 2 — Window function over an aggregate: share of total
-- GROUP BY runs first (one count per source), then sum(...) OVER ()
-- adds those counts across ALL result rows. Empty OVER () = one window
-- containing every row, so the grand total repeats on each row.
-- -------------------------------------------------------------
SELECT
    source,
    count(*)                                              AS contacts,
    sum(count(*)) OVER ()                                 AS total_contacts,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1)    AS pct_of_total
FROM contacts
GROUP BY source
ORDER BY contacts DESC;


-- -------------------------------------------------------------
-- Ex 3 — CTE to PROVE a total instead of eyeballing it
-- Lesson: rounding each part separately can make the total drift from
-- 100 (e.g. 3 equal parts -> 33+33+33 = 99). Fewer decimals = more drift.
-- -------------------------------------------------------------
WITH by_source AS (
    SELECT
        source,
        count(*) AS contacts,
        round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct_of_total
    FROM contacts
    GROUP BY source
)
SELECT
    count(*)          AS n_sources,
    sum(contacts)     AS total_contacts,
    sum(pct_of_total) AS total_pct
FROM by_source;


-- -------------------------------------------------------------
-- Ex 4 — LEFT JOIN + aliases to test a hypothesis
-- Hypothesis: "recent batches of one source have worse email coverage".
-- LEFT JOIN keeps every contact even when its batch is missing from the
-- log (b.* comes back NULL); an INNER JOIN would silently drop them.
-- WHERE filters before GROUP BY. Result: hypothesis NOT supported, and
-- every batch joined to NULL -> the batch log was never being written.
-- -------------------------------------------------------------
SELECT
    c.source_batch,
    b.started_at::date                          AS imported_on,
    count(*)                                    AS contacts,
    count(c.email)                              AS with_email,
    round(100.0 * count(c.email) / count(*), 1) AS pct_with_email
FROM contacts c
LEFT JOIN import_batches b
       ON b.source_batch = c.source_batch
WHERE c.source = 'smartlead'
GROUP BY c.source_batch, b.started_at
ORDER BY b.started_at NULLS LAST;


-- -------------------------------------------------------------
-- Ex 5/6 — Inspect the pipeline's own audit tables
-- Empty result = table has no rows (a permissions problem would raise
-- "permission denied", not return 0 rows). jsonb_array_length counts
-- items in a JSON list; ::text + left() previews a JSON cell.
-- -------------------------------------------------------------
SELECT source_batch, source_name, rows_in, rows_written, rows_dropped, started_at
FROM import_batches
ORDER BY started_at;

SELECT
    source_name,
    status,
    model,
    created_at::date                  AS created_on,
    jsonb_array_length(extra_fields)  AS n_extra_fields,
    left(headers::text, 80)           AS headers_preview
FROM header_maps
ORDER BY source_name, created_at;
