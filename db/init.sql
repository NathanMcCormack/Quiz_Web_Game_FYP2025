-- Create the two service databases the first time Postgres initializes.
-- This runs only on a fresh pgdata volume.

CREATE DATABASE game_db;
CREATE DATABASE user_db;