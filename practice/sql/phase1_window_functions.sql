-- Phase 1: Window Functions
-- Practice against the "trips" table in the de_practice Postgres database.

-- ============================================================
-- Exercise 1: Rank trips by duration within each station (ROW_NUMBER)
-- ============================================================

SELECT
    start_station,
    duration_seconds,
    ROW_NUMBER() OVER (PARTITION BY start_station ORDER BY duration_seconds DESC) AS rank_in_station
FROM trips
ORDER BY start_station, rank_in_station;
-- PARTITION BY resets the numbering per station; ORDER BY inside OVER() decides
-- what "rank 1" means (here: longest trip). Confirmed: numbering restarts at 1
-- for each new station, rank 1 = longest duration in that station.


-- ============================================================
-- Exercise 2: Compare each trip's duration to the previous trip's (LAG)
-- ============================================================

SELECT
    start_date,
    duration_seconds,
    LAG(duration_seconds) OVER (ORDER BY start_date) AS prev_duration
FROM trips
ORDER BY start_date;
-- LAG grabs the value from the row before the current one, in the sequence
-- defined by OVER(ORDER BY ...) -- independent from any outer ORDER BY.
-- First row is NULL (nothing precedes it). Confirmed correct.


-- ============================================================
-- Exercise 3: Running total of trip duration (SUM as a window function)
-- ============================================================

-- First attempt: default frame (RANGE) -- ties on start_date get grouped
-- together and share the same cumulative total instead of incrementing
-- row by row. Useful to know, but usually NOT what you want.
SELECT
    start_date,
    duration_seconds,
    SUM(duration_seconds) OVER (ORDER BY start_date) AS running_total_ranged
FROM trips
ORDER BY start_date;

-- Correct version for a strict row-by-row running total regardless of ties:
SELECT
    start_date,
    duration_seconds,
    SUM(duration_seconds) OVER (
        ORDER BY start_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM trips
ORDER BY start_date;
-- Confirmed correct: climbs one row at a time (420, 1030, 1410, 2310, 2850, ...)
-- ROWS = "this row and everything strictly before it, one at a time" --
-- overrides the default RANGE frame's tie-grouping behavior.

-- Variant: partitioned running total (one per station instead of one overall)
SELECT
    start_date,
    duration_seconds,
    start_station,
    SUM(duration_seconds) OVER (
        PARTITION BY start_station
        ORDER BY start_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM trips
ORDER BY start_date;
-- PARTITION BY resets the running total per station -- each station accumulates
-- independently instead of sharing one continuous total.
