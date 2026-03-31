SHOW TABLES;

DESCRIBE all_flights;

SELECT * FROM all_flights;

CREATE TABLE all_flights_cleansed (
  poll_timestamp TIMESTAMP_LTZ(0),
  icao24 STRING,
  callsign STRING,
  origin_country STRING,
  event_timestamp TIMESTAMP_LTZ(0),
  longitude DECIMAL(10, 4),
  latitude DECIMAL(10, 4),
  barometric_altitude DECIMAL(10, 2),
  on_ground BOOLEAN,
  velocity_m_per_s DECIMAL(10, 2)
);

INSERT INTO all_flights_cleansed
SELECT
  TO_TIMESTAMP_LTZ(`time`, 0) AS poll_timestamp,
  state.icao24 AS icao24,
  RTRIM(state.callsign) AS callsign,
  state.origin_country AS origin_country,
  TO_TIMESTAMP_LTZ(CAST(state.last_contact AS BIGINT), 0) AS event_timestamp,
  CAST(state.longitude AS DECIMAL(10, 4)) AS longitude,
  CAST(state.latitude AS DECIMAL(10, 4)) AS latitude,
  CAST(state.baro_altitude AS DECIMAL(10, 2)) AS barometric_altitude,
  state.on_ground AS on_ground,
  CAST(state.velocity AS DECIMAL(10, 2)) AS velocity_m_per_s
FROM all_flights
CROSS JOIN UNNEST(all_flights.states) AS states_table (state);

SELECT * FROM all_flights_cleansed;
