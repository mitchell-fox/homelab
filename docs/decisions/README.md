# Architecture Decision Records

Each ADR records one decision: the context, the options considered, what was chosen, and what it costs.
ADRs are not edited after they are accepted. To change a decision, write a new ADR that supersedes the old one.

| ADR | Decision | Status |
|-----|----------|--------|
| [0001](ADR-0001-terraform.md) | Terraform for infrastructure as code | Accepted |
| [0002](ADR-0002-azure-state-backend.md) | Terraform state in Azure Storage | Accepted |
| [0003](ADR-0003-single-source-of-truth.md) | `inventory/network.yaml` as the single source of truth | Accepted |
| [0004](ADR-0004-sops-age-secrets.md) | Secrets encrypted with sops + age | Accepted |
| [0005](ADR-0005-proxmox-over-esxi.md) | Migrate the hypervisor from ESXi to Proxmox | Accepted |
| [0006](ADR-0006-k3s-flux-gitops.md) | k3s + Flux for workloads | Accepted |
| [0007](ADR-0007-dns-outside-cluster.md) | DNS on the Pi, outside the cluster | Accepted |
