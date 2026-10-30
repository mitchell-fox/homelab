# ADR-0007: DNS on the Pi, outside the cluster

- Status: Accepted
- Date: 2026-10-30

## Context
Every device on the network depends on DNS. If DNS runs on the cluster, a cluster or hypervisor
outage takes down name resolution for the whole house.

## Options
- **DNS in k3s**: one deployment model, but resolution fails along with the cluster.
- **DNS on the UniFi router**: survives outages, but its local-record support is limited and harder to drive from code.
- **AdGuard Home or Pi-hole on the Raspberry Pi**: independent hardware with low power draw,
  configured by Ansible from `network.yaml`.

## Decision
DNS runs on the Pi, configured by Ansible, with records generated from `inventory/network.yaml`.
The choice between AdGuard Home and Pi-hole is made in step 3.

## Consequences
- The Pi is a single point of failure for DNS. Mitigate by handing out the router as secondary DNS via DHCP.
- A second, Ansible-managed deployment model sits alongside Flux. That's an intentional split between
  core network services and applications.
