-- Phase 1: Query Performance Basics (Indexes + EXPLAIN)
-- Practice against a synthetic 200k-row table in the de_practice Postgres database.

-- ============================================================
-- Setup: generate a large synthetic table (trips table is only 20 rows --
-- too small for Postgres to ever bother using an index)
-- ============================================================

CREATE TABLE trips_big AS
SELECT
    trip_id,
    (ARRAY['Union Station','Dupont Circle','Georgetown','Capitol Hill'])[1 + floor(random()*4)] AS start_station,
    (ARRAY['Union Station','Dupont Circle','Georgetown','Capitol Hill'])[1 + floor(random()*4)] AS end_station,
    (300 + floor(random()*900))::int AS duration_seconds,
    (DATE '2026-01-01' + floor(random()*300)::int) AS start_date
FROM generate_series(1, 200000) AS trip_id;


-- ============================================================
-- Exercise: before/after comparison -- Seq Scan vs indexed lookup
-- ============================================================

-- Baseline, no index: Seq Scan, ~44.56 ms execution time,
-- scanned all 200,000 rows (50,197 matched / 149,803 filtered out)
EXPLAIN ANALYZE
SELECT * FROM trips_big WHERE start_station = 'Union Station';

-- Add an index on the filtered column
CREATE INDEX idx_trips_big_station ON trips_big(start_station);
-- (use CREATE INDEX IF NOT EXISTS if re-running this script -- an index is a
-- permanent object, re-running CREATE INDEX on an existing one errors out)

-- Re-run the same query: Bitmap Heap Scan + Bitmap Index Scan, ~5.06 ms
-- (~9x faster). At this ~25% selectivity (1 of 4 stations), Postgres chose
-- a bitmap scan rather than a plain Index Scan or Seq Scan -- a middle-ground
-- plan: use the index to find which pages have matches (skip the rest),
-- then read those pages in physical order (avoid the random-I/O cost of a
-- plain index scan). Heap Blocks: exact=1667 shows it only touched 1,667
-- pages instead of the full table.
EXPLAIN ANALYZE
SELECT * FROM trips_big WHERE start_station = 'Union Station';

-- Note: an index is not a table and not queryable -- confirmed by trying
-- `SELECT * FROM idx_trips_big_station` -> ERROR: "idx_trips_big_station" is
-- an index. It's a lookup structure Postgres uses internally, not a data source.
