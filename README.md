# OpenSky HTTP Streaming Relay Demo

This repository turns the OpenSky REST API into a reproducible Confluent Cloud streaming demo.

It preserves the spirit of Confluent's original `demo-scene/http-streaming` walkthrough, but replaces the managed HTTP Source connector with a local relay that polls OpenSky and publishes snapshots into Kafka using the Confluent CLI.

## Why This Repo Exists

The original demo is a strong concept, but the managed connector path is not reliable in every environment today:

- the legacy HTTP Source connector configuration is stale
- the newer HTTP Source V2 connector may still fail if the managed runtime cannot reach `opensky-network.org`

This repo keeps the same use case and exploration flow while making ingestion deterministic and reproducible.

## What This Demo Does

- polls `https://opensky-network.org/api/states/all`
- limits results to the original Switzerland-focused bounding box
- normalizes the OpenSky array payload into named fields
- publishes one snapshot per poll to Kafka topic `all_flights`
- registers a JSON Schema for the topic value
- walks through the same Flink SQL shaping and cleansing story as the original demo

## Repository Contents

- `relay_opensky.py`: local OpenSky-to-Kafka relay
- `opensky_poll.schema.json`: schema for Kafka values
- `.env.example`: runtime configuration template
- `sql/flink_demo.sql`: Flink SQL statements for exploration and cleansing
- `img/`: images adapted from the original demo for the walkthrough
- `ATTRIBUTION.md`: upstream attribution and adaptation notes

## Prerequisites

- Python 3
- Confluent CLI installed and authenticated
- A Confluent Cloud environment
- A Kafka cluster
- A Flink compute pool
- Kafka API credentials for the cluster
- Schema Registry credentials with subject registration access

## Suggested Confluent Cloud Setup

You can reuse an existing environment or create a fresh one for isolation.

Typical resources:

- Kafka cluster: `http-streaming_kafka-cluster`
- Flink compute pool: `http-streaming`
- Topic: `all_flights`

Create the topic if it does not already exist:

```bash
confluent kafka topic create all_flights --cluster <KAFKA_CLUSTER_ID> --environment <ENVIRONMENT_ID>
```

## Relay Setup

1. Copy `.env.example` to `.env`.
2. Fill in:
   - `BOOTSTRAP_SERVERS`
   - `KAFKA_API_KEY`
   - `KAFKA_API_SECRET`
   - `SCHEMA_REGISTRY_URL`
   - `SCHEMA_REGISTRY_API_KEY`
   - `SCHEMA_REGISTRY_API_SECRET`
   - `TOPIC`
3. Leave `POLL_INTERVAL_SECONDS=60` unless you want a different cadence.

## Run The Relay

```bash
python3 relay_opensky.py
```

If successful, you will see output like:

```text
Polling OpenSky every 60s and producing to all_flights
Successfully registered schema with ID "100043".
snapshot_time=1774975712 states=88
```

## Validate Data In Confluent Cloud

Open your Confluent Cloud environment and Kafka cluster, then confirm the topic exists and messages are arriving.

Useful original reference screens:

![Cluster](img/cc-cluster.png)

![Topic](img/cc-topic.png)

You can also consume from the topic directly:

```bash
confluent kafka topic consume all_flights \
  --bootstrap <BOOTSTRAP_SERVERS> \
  --api-key <KAFKA_API_KEY> \
  --api-secret <KAFKA_API_SECRET> \
  --value-format jsonschema \
  --schema-registry-endpoint <SCHEMA_REGISTRY_URL> \
  --schema-registry-api-key <SCHEMA_REGISTRY_API_KEY> \
  --schema-registry-api-secret <SCHEMA_REGISTRY_API_SECRET> \
  --from-beginning
```

## Explore Raw Data In Flink

Once the relay is publishing, `all_flights` becomes available to Flink.

The relay publishes a cleaner structure than the original connector path:

- `time`
- `states` as an array of typed flight-state objects

You can start with:

```sql
SHOW TABLES;
DESCRIBE all_flights;
SELECT * FROM all_flights;
```

If you want a step-by-step walkthrough, use the statements in `sql/flink_demo.sql`.

The original demo entered through a connector validation step:

![Flink compute pool](img/cc-flink-compute-pool.png)

## Shape And Cleanse Data With Flink

The original demo story still applies:

1. each poll contains many flights
2. downstream consumers want one aircraft per row
3. fields should be typed and trimmed into a more usable table

This repo includes a Flink SQL script that creates `all_flights_cleansed` and inserts one row per aircraft from each snapshot.

The original bounding box remains the same:

![Switzerland bounding box](img/bounding-box.png)

## Why The Flink SQL Changed Slightly

The original connector landed `states` as an array of arrays, so the SQL had to address values by position.

This relay publishes named fields instead, which makes the table easier to understand and the downstream SQL more maintainable. The demo outcome is the same, but the raw landing format is better.

## Tear Down

When you are done, stop the relay with `Ctrl-C`.

Then clean up the cloud resources you created for the demo:

- delete the topic if it is demo-only
- delete the Kafka cluster if it is demo-only
- delete the Flink compute pool if it is demo-only
- revoke or delete any temporary API keys you created

## Attribution

This repository adapts the original Confluent `demo-scene/http-streaming` demo and carries forward part of its narrative structure and visual assets under Apache 2.0 terms.

See `ATTRIBUTION.md` and `LICENSE`.
