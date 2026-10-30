# homelab

My home network, private cloud, and cluster, defined as code. Fully offline and self-hosted at $0, using the
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
| Secrets | sops + age for bootstrap, OpenBao at runtime (step 5) | [ADR-0004](docs/decisions/ADR-0004-sops-age-secrets.md), [ADR-0014](docs/decisions/ADR-0014-secrets-two-layers.md) |
| Git hosting | Private Forgejo (fitlet2), public GitHub mirror via Copybara | [ADR-0012](docs/decisions/ADR-0012-private-forgejo-public-mirror.md), [ADR-0013](docs/decisions/ADR-0013-git-server-backups.md) |
| Host config | Ansible behind `make`, inventory from `network.yaml` | [ADR-0011](docs/decisions/ADR-0011-ansible-entry-point.md) |
| Runbooks | One per role, shared procedures in `common/` | [ADR-0010](docs/decisions/ADR-0010-runbooks.md) |
| Private cloud | OpenStack on bare metal (Kolla-Ansible) | [ADR-0016](docs/decisions/ADR-0016-openstack-on-bare-metal.md) |
| Host roles | Pi: DNS · fitlet2: git + vault · i9: workloads | [ADR-0017](docs/decisions/ADR-0017-host-roles.md) |
| Workloads | k3s + Flux | [ADR-0006](docs/decisions/ADR-0006-k3s-flux-gitops.md) |
| DNS | AdGuard Home / Pi-hole on a Raspberry Pi | [ADR-0007](docs/decisions/ADR-0007-dns-outside-cluster.md) |
| Local LLM | llama.cpp (Vulkan) + Open WebUI on a bare-metal laptop | [ADR-0009](docs/decisions/ADR-0009-llm-host.md) |

## Layout

```
inventory/network.yaml   source of truth: subnet, DHCP, hosts, IPs, MACs
terraform/unifi/         networks, DHCP reservations, firewall, WLANs
openstack/               Kolla-Ansible config for the single-node OpenStack
terraform/openstack/     networks, images, flavors, k3s instances
ansible/                 inventory script, roles (llm, git, dns, ...), group_vars per role
Makefile                 entry point: make llm, make dns, make all, ...
copy.bara.sky            Copybara config for the public GitHub mirror
clusters/                Flux manifests
secrets/                 sops-encrypted only
docs/decisions/          architecture decision records
docs/ideas.md            backlog of future ideas (not yet decided)
docs/runbooks/           step-by-step procedures for humans (rebuild, update, rotate, recover)
docs/learning/           study notes behind the decisions (not decisions themselves)
```

## Roadmap

- [x] 1. Repo, source of truth, secrets, local Terraform state
- [ ] 2. UniFi in Terraform (import the existing config, don't recreate it)
- [ ] 3. Pi DNS via Ansible, with records generated from `network.yaml`
- [ ] 4. OpenStack on the i9 box (Kolla-Ansible), VMs as code
- [ ] 5. k3s + Flux, then move services in one at a time
- [ ] 6. DR test: wipe something on purpose, rebuild from the repo, measure the time
