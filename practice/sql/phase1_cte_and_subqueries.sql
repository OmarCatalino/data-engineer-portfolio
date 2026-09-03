-- Phase 1: CTEs & Subqueries
-- Practice against the "trips" table in the de_practice Postgres database.
-- Convention: each exercise gets a short title comment, then the query.
-- Add new exercises to the bottom of this file as you go.

-- ============================================================
-- Exercise 1+2: Trips above average duration (subquery vs CTE)
-- ============================================================

-- Version A: plain subquery
SELECT *
FROM trips
WHERE duration_seconds > (
    SELECT AVG(duration_seconds) FROM trips
);

-- Version B: same thing as a CTE
WITH avg_duration AS (
    SELECT AVG(duration_seconds) AS avg_dur FROM trips
)
SELECT trips.*
FROM trips, avg_duration
WHERE trips.duration_seconds > avg_duration.avg_dur;


-- ============================================================
-- Exercise 3: Stations with more than 3 trips (CTE + filtered aggregate)
-- ============================================================

-- TODO
