# ADR-0005: Migrate the hypervisor from ESXi to Proxmox

- Status: Superseded by [ADR-0016](ADR-0016-openstack-on-bare-metal.md)
- Date: 2026-10-30

## Context
VMs should be defined as code and built from cloud-init templates. The current ESXi host is on the free license.

## Options
- **Stay on free ESXi**: its API is read-only for writes, so Terraform can't manage VMs. Broadcom has also
  ended or limited free ESXi licensing, so its future is uncertain.
- **Proxmox VE**: free, with a full REST API, the well-maintained bpg/proxmox Terraform provider,
  first-class cloud-init support, and a built-in ESXi import wizard for migration.
- **Bare-metal k3s, no hypervisor**: simpler, but loses snapshots and the ability to run non-Kubernetes VMs.

## Decision
Proxmox VE. Existing VMs move over with the ESXi import wizard, and new VMs come from cloud-init templates via Terraform.

## Consequences
- A one-time migration with downtime. Its scope depends on what runs on the ESXi box today (open question).
