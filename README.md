# Cloud Linux Observability & Telemetry Pipeline

An end-to-end infrastructure monitoring and observability project built on Oracle Cloud Infrastructure (OCI) and Grafana Cloud. This project demonstrates Linux administration, least-privilege cloud governance, REST API / JSON telemetry collection, time-series visualization, alerting, and operational runbook documentation.

## Architecture Overview

```text
[OCI Sub-Compartment: observability-lab]
  └── [Ubuntu LTS Compute Instance]
        ├── System Metrics & Logs (Grafana Alloy / Node Exporter) ──┐
        └── Python REST/JSON Health Check (systemd timer) ─────────┼──> [Grafana Cloud]
                                                                         ├── Dashboards
                                                                         └── Alert Rules -> Runbook Triage
