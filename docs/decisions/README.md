# Architecture Decision Records

Each ADR records one decision: the context, the options considered, what was chosen, and what it costs.
ADRs are not edited after they are accepted. To change a decision, write a new ADR that supersedes the old one.

| ADR | Decision | Status |
|-----|----------|--------|
| [0001](ADR-0001-terraform.md) | Terraform for infrastructure as code | Accepted |
| [0002](ADR-0002-azure-state-backend.md) | Terraform state in Azure Storage | Superseded by 0008 |
| [0003](ADR-0003-single-source-of-truth.md) | `inventory/network.yaml` as the single source of truth | Accepted |
| [0004](ADR-0004-sops-age-secrets.md) | Secrets encrypted with sops + age | Accepted, amended by 0015 and 0019 |
| [0005](ADR-0005-proxmox-over-esxi.md) | Migrate the hypervisor from ESXi to Proxmox | Superseded by 0016 |
| [0006](ADR-0006-k3s-flux-gitops.md) | k3s + Flux for workloads | Accepted |
| [0007](ADR-0007-dns-outside-cluster.md) | DNS on the Pi, outside the cluster | Accepted |
| [0008](ADR-0008-local-terraform-state.md) | Terraform state local, then self-hosted Postgres | Accepted |
| [0009](ADR-0009-llm-host.md) | LAN LLM host on bare metal: llama.cpp on Vulkan, Open WebUI | Accepted |
| [0010](ADR-0010-runbooks.md) | Runbooks per role, shared procedures in `common/` | Accepted |
| [0011](ADR-0011-ansible-entry-point.md) | `make` over Ansible, inventory generated from `network.yaml` | Accepted |
| [0012](ADR-0012-private-forgejo-public-mirror.md) | Private Forgejo as source of truth, public GitHub mirror via Copybara | Accepted, amended by 0017 |
| [0013](ADR-0013-git-server-backups.md) | Git server backups with restic to microSD and a second machine | Accepted |
| [0014](ADR-0014-secrets-two-layers.md) | Secrets in two layers (sops bootstrap, OpenBao runtime); config in git | Accepted, amended by 0017 and 0019 |
| [0015](ADR-0015-age-key-in-tpm.md) | Workstation age key in the TPM, backup key in the password manager | Accepted |
| [0016](ADR-0016-openstack-on-bare-metal.md) | OpenStack on bare metal (Kolla-Ansible) on the i9 box; rebuild, don't migrate | Accepted |
| [0017](ADR-0017-host-roles.md) | One job per box: Pi DNS, fitlet2 git + vault, i9 workloads | Accepted |
| [0018](ADR-0018-pihole-in-docker.md) | Pi-hole in Docker Compose on the Pi, with HaGeZi Multi PRO++ and threat feeds | Accepted |
| [0019](ADR-0019-secrets-out-of-public-repo.md) | Secrets stay out of the public repo, even encrypted | Accepted |
