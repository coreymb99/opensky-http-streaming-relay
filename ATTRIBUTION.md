This repository is an adaptation of the `http-streaming` demo from Confluent's `demo-scene` repository.

Upstream source:

- https://github.com/confluentinc/demo-scene/tree/master/http-streaming

Adapted elements:

- demo structure and overall walkthrough
- parts of the documentation narrative
- image assets under `img/`
- the OpenSky use case and bounding box

Major changes in this repository:

- replaced the managed HTTP Source connector path with a local relay
- updated the ingestion path to publish directly into Confluent Cloud via the Confluent CLI
- changed the landing schema to a named JSON Schema payload
- added a new standalone README and Flink SQL flow for the relay-based variant

The upstream repository is licensed under Apache License 2.0. This repository includes the Apache 2.0 license text in `LICENSE`.
