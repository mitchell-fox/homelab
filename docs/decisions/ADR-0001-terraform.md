# ADR-0001: Terraform for infrastructure as code

- Status: Accepted
- Date: 2026-10-30

## Context
The network (UniFi) and the hypervisor (Proxmox) need to be managed declaratively, so that a change
like Spectrum's forced subnet move is a reviewed diff instead of an afternoon of clicking.

## Options
- **Terraform**: mature community providers for UniFi and Proxmox (bpg/proxmox). Widely asked for in job listings.
- **OpenTofu**: same HCL and providers, open-source license. Less common in job listings.
- **Bicep**: what I use at work, but it only targets Azure and can't manage UniFi or Proxmox.
- **Ansible only**: works, but it's procedural, so there's no plan/diff and no drift detection from state.

## Decision
Terraform.

## Consequences
- The BSL license doesn't matter for personal use. Switching to OpenTofu later is close to a drop-in.
- The UniFi provider is community-maintained, so its coverage has to be checked against my controller
  version and any gaps written down (see step 2 of the rollout).
