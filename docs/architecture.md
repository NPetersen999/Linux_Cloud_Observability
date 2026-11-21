# Cloud Architecture & Design Decisions

## 1. Cloud Platform & Compute Selection
* **Provider:** Oracle Cloud Infrastructure (OCI) Always Free Tier.
* **Operating System:** Canonical Ubuntu LTS (Standard Image) chosen for stability, broad `apt` package support, `systemd` service management, and alignment with standard enterprise Linux environments.
* **Compute Shape:** Always Free virtual machine instance sized for lightweight telemetry agent execution and scheduled Python scripts without local hardware dependencies.

## 2. IAM & Compartment Isolation (Access Controls)
* **Decision:** Moved all project resources (VCN, subnets, security lists, and compute instance) out of the root tenancy compartment into a dedicated sub-compartment (`observability-lab`).
* **Rationale:**
  * Follows least-privilege cloud governance by separating workload resources from root tenancy administration.
  * Establishes a clean boundary for IAM policies, resource auditing, and cost/quota tracking.
  * Simplifies lifecycle management and clean teardown without impacting unrelated tenancy resources.

## 3. Addressing, VLSM & Subnet Placement
* **VCN Block:** `10.10.0.0/24` (256 total IPv4 addresses) inside `Observability_Lab_VCN`.
* **Subnet Allocation (`10.10.0.240/28`):** Placed the `/28` lab subnet (13 usable host IPs in OCI after reserved network, gateway, and broadcast/reserved addresses) at the upper end of the `/24` range rather than `10.10.0.0/28`.
* **VLSM Rationale:** Placing the small `/28` at the top of the range preserves contiguous lower address space (`10.10.0.0`–`10.10.0.239`) so larger future subnets—such as a `/25`—can be allocated cleanly without fragmentation or re-addressing existing hosts.
* **Public Subnet Selection:** Configured the lab subnet as a **Public Subnet** so `Observability_Lab_Linux` can receive a public IPv4 address for SSH access and ship telemetry outbound over HTTPS to Grafana Cloud without needing a separate NAT Gateway or Bastion host for a minimal lab footprint.

## 4. Network & Host Security Controls
* **Cloud Perimeter (OCI Security Lists):**
  * Restricted inbound TCP Port `22` (SSH) strictly to the administrator's single public IP (`<ADMIN_IP>/32`) rather than `0.0.0.0/0`.
  * Left outbound HTTPS (`443`) open for OS security updates, external REST API polling, and outbound telemetry shipping to Grafana Cloud—eliminating the need to expose inbound monitoring ports to the public internet.
* **Host-Level Hardening (Ubuntu):**
  * Enforced SSH key-pair authentication (`PasswordAuthentication no`).
  * Enabled `ufw` host firewall with default-deny inbound policy and explicit `OpenSSH` allowance.
  * Verified DNS resolution (`dig`) and outbound TLS connectivity (`curl`) prior to agent deployment.

## 5. Telemetry & Data Flow Architecture
* **Push-Based Telemetry Model:** The Ubuntu host pushes host metrics, system logs, and custom JSON health metrics outbound over HTTPS to Grafana Cloud.
* **Collection Interval:** Configured at 30–60 second intervals to maintain high visibility into service health while staying well within free-tier bandwidth and active-series limits.
