DROP TABLE IF EXISTS post;

CREATE TABLE
  water (
    id INTEGER PRIMARY key autoincrement,
    logged_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sensor TEXT NOT NULL,
    gauge_value INTEGER NOT NULL,
    meter_value INTEGER NOT NULL
  );