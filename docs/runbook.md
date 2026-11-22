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
