# homelab

My home network, hypervisor, and cluster, defined as code. Fully offline and self-hosted at $0, using the
open-source tools Azure runs on or mirrors (Flux, Prometheus, Postgres) so the skills carry over to work.

My ISP swapped my equipment and forced a renumbering from `192.168.1.0/24` to `192.168.10.0/24`.
This repo exists so that the next change like that is a one-line diff to
[`inventory/network.yaml`](inventory/network.yaml), followed by `terraform apply` and an Ansible run.

## Stack

| Layer | Tool | Why |
|-------|------|-----|
| Network (UniFi) | Terraform | [ADR-0001](docs/decisions/ADR-0001-terraform.md) |
| Terraform state | Local, then self-hosted Postgres | [ADR-0008](docs/decisions/ADR-0008-local-terraform-state.md) |
| Source of truth | `inventory/network.yaml` | [ADR-0003](docs/decisions/ADR-0003-single-source-of-truth.md) |
| Secrets | sops + age | [ADR-0004](docs/decisions/ADR-0004-sops-age-secrets.md) |
| Hypervisor | Proxmox VE | [ADR-0005](docs/decisions/ADR-0005-proxmox-over-esxi.md) |
| Workloads | k3s + Flux | [ADR-0006](docs/decisions/ADR-0006-k3s-flux-gitops.md) |
| DNS | AdGuard Home / Pi-hole on a Raspberry Pi | [ADR-0007](docs/decisions/ADR-0007-dns-outside-cluster.md) |

## Layout

```
inventory/network.yaml   source of truth: subnet, DHCP, hosts, IPs, MACs
terraform/unifi/         networks, DHCP reservations, firewall, WLANs
terraform/proxmox/       VMs from cloud-init templates
ansible/                 Pi DNS, k3s bootstrap
clusters/                Flux manifests
secrets/                 sops-encrypted only
docs/decisions/          architecture decision records
docs/runbooks/           step-by-step procedures for humans (rebuild, update, rotate, recover)
```

## Roadmap

- [ ] 1. Repo, source of truth, secrets, local Terraform state
- [ ] 2. UniFi in Terraform (import the existing config, don't recreate it)
- [ ] 3. Pi DNS via Ansible, with records generated from `network.yaml`
- [ ] 4. Proxmox migration, VMs as code
- [ ] 5. k3s + Flux, then move services in one at a time
- [ ] 6. DR test: wipe something on purpose, rebuild from the repo, measure the time
