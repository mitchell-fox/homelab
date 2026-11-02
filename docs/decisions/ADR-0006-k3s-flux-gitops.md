# ADR-0006: k3s + Flux for workloads

- Status: Accepted
- Date: 2026-10-30

## Context
Self-hosted services need a deployment model where git is the source of truth, consistent with the rest of the repo.

## Options
- **Coolify / Portainer**: quick to start, but config lives in their own database and UI, which breaks the single source of truth.
- **Docker Compose plus Ansible**: simple, but it's push-based and doesn't reconcile drift.
- **k3s + Argo CD**: a strong option. Its UI is nice, but it's heavier.
- **k3s + Flux**: pull-based GitOps that reconciles from this repo, decrypts sops natively, and is
  the engine behind AKS GitOps, which ties to my Azure work.

## Decision
A 3-node k3s cluster on Proxmox VMs, reconciled by Flux from `clusters/`.

## Consequences
- More moving parts than Compose. The learning value is worth it.
- VM sizing waits on the ESXi host's specs (open question).
