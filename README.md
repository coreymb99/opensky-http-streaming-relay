# OpenSky HTTP Streaming Relay

This project polls the OpenSky REST API on a fixed interval and publishes each snapshot into Confluent Cloud as a schema-managed Kafka record.

It exists as a practical replacement for the older managed HTTP Source Connector flow in the original `demo-scene/http-streaming` demo, which may fail when the managed connector runtime cannot reach the public OpenSky endpoint.

## What It Does

- Calls `https://opensky-network.org/api/states/all`
- Limits results to the original Switzerland-focused bounding box from the demo
- Normalizes the OpenSky array payload into named fields
- Produces one snapshot per poll into Kafka
- Registers and uses a JSON Schema subject for the topic value

## Prerequisites

- Python 3
- The Confluent CLI installed and authenticated
- A Kafka topic in Confluent Cloud, for example `all_flights`
- Kafka API credentials for that cluster
- Schema Registry API credentials with permission to register subjects

## Setup

1. Copy `.env.example` to `.env`.
2. Fill in your Kafka and Schema Registry credentials.
3. Adjust `TOPIC` or `POLL_INTERVAL_SECONDS` if needed.

## Run

```bash
python3 relay_opensky.py
```

The script will continue polling until you stop it with `Ctrl-C`.

## Files

- `relay_opensky.py`: polling and produce loop
- `opensky_poll.schema.json`: JSON Schema used for the Kafka value
- `.env.example`: runtime configuration template

## Notes

- The script uses only the Python standard library plus the `confluent` CLI.
- No secrets are stored in the repo by default.
- If the topic already has an incompatible schema under the same subject, you may need to clear or change that subject before first publish.
