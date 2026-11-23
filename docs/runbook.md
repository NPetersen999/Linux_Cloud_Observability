## Telemetry & Fault-Trace Runbook
* **Check Collector & Timer Health:**
  ```bash
  systemctl status alloy api-health-check.timer --no-pager
  systemctl list-timers api-health-check.timer --no-pager
  sudo journalctl -u alloy -u api-health-check.service -n 20 --no-pager
* **Controlled Failure Test**
  ```bash
  sudo systemctl stop alloy
  journalctl -u api-health-check.service -n 10 --no-pager
  systemctl is-active alloy || true
  systemctl status alloy --no-pager
  sudo systemctl start alloy
  journalctl -u api-health-check.service -n 10 --no-pager
* **Configure Alloy for Grafana API connection**
  ```bash
  sudo tee /etc/alloy/config.alloy > /dev/null <<'EOF'
  logging {
    level  = "info"
    format = "logfmt"
  }

  prometheus.exporter.unix "host_metrics" {
    include_exporter_metrics = true
  }

  prometheus.scrape "scrape_host_metrics" {
    targets         = prometheus.exporter.unix.host_metrics.targets
    forward_to      = [prometheus.remote_write.grafana_cloud.receiver]
    scrape_interval = "15s"
  }

  prometheus.remote_write "grafana_cloud" {
    endpoint {
      url = env("GRAFANA_PROM_URL")

      basic_auth {
        username = env("GRAFANA_PROM_USER")
        password = env("GRAFANA_CLOUD_TOKEN")
      }
    }
  }

  local.file_match "system_logs" {
    path_targets = [
      {
        "__path__" = "/var/log/auth.log",
        "job"      = "auth_log",
        "host"     = "observability-lab-linux",
      },
      {
        "__path__" = "/var/log/observability_api_check.jsonl",
        "job"      = "api_health_check",
        "host"     = "observability-lab-linux",
      },
    ]
  }

  loki.source.file "tail_logs" {
    targets    = local.file_match.system_logs.targets
    forward_to = [loki.write.grafana_cloud.receiver]
  }

  loki.write "grafana_cloud" {
    endpoint {
      url = env("GRAFANA_LOKI_URL")

      basic_auth {
        username = env("GRAFANA_LOKI_USER")
        password = env("GRAFANA_CLOUD_TOKEN")
      }
    }
  }
  EOF
