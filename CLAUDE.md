# Homelab as code

Rebuild and codify my home network. Spectrum swapped my equipment, which forced a subnet change from
192.168.1.0/24 to 192.168.10.0/24. The goal: the next change like that is a one-line diff.
It's also meant to be an interview talking point, so design decisions get written down as ADRs.

## Hardware

- UniFi router (exact model / where the controller runs: TBD)
- i9 box (was ESXi, wiped; old VMs rebuilt from code): i9-12900HK (14C/20T), 64 GB RAM, 2 TB NVMe, 1 TB SATA HDD
  (Cinder volumes: Jellyfin media), 2 NICs. Ubuntu Server 24.04 LTS + OpenStack (ADR-0016).
- Raspberry Pi 4, 8 GB (DNS)
- Additional Raspberry Pis (count and models: TBD)
- fitlet2, 8 GB RAM, 128 GB no-name SATA SSD (to confirm), microSD slot for local backups, Ubuntu Server 26.04 LTS
  (same as the LLM box, so roles target one distro): Forgejo + OpenBao (ADR-0017)
- LLM box (a laptop, run lid-closed): Ryzen 7 2700, 64 GB RAM, Radeon RX Vega 56 (8 GB), 480 GB SATA SSD,
  Ubuntu Server
- Spare: 500 GB NVMe SSD, no home yet
- Workstation (desktop, `mitch-desktop-linux`): Ryzen 9 5900XT, 64 GB RAM, GeForce RTX 5060 Ti (16 GB), CachyOS.
  Runs Terraform, Ansible and sops; TPM 2.0. Not part of the lab itself.

## Hard constraint: offline, free, local

Everything runs on my own hardware and network, at $0. No cloud services, no paid tiers, no "free for 12 months".
Azure is the inspiration, not the platform: where there's a choice, pick the self-hosted tool closest to what
Azure uses or runs underneath (Flux = AKS GitOps, Prometheus/Grafana = Azure Monitor managed services, Postgres =
Azure Database for PostgreSQL), so homelab work keeps building the skills I use at work.

## Decisions so far

- **Terraform** (not OpenTofu): same HCL, and matches job listings. Bicep can't manage UniFi or OpenStack.
- **Terraform state stays local** (ADR-0008, supersedes the Azure Storage plan in ADR-0002). Local file for now,
  then the `pg` backend on lab-hosted Postgres.
- **OpenStack on bare metal on the i9 box** (ADR-0016, supersedes Proxmox in ADR-0005): Kolla-Ansible from the
  workstation (`make openstack`), single node, Ubuntu 24.04 (newest Kolla 2026.1 supports; 26.04 later). NIC 1 =
  management, NIC 2 = Neutron external. Everything on top via the Terraform `openstack` provider. The old ESXi VMs
  were rebuilt from code, not migrated. Runner-up: Incus.
- **One job per box** (ADR-0017): Pi = DNS, fitlet2 = Forgejo + OpenBao (own age key scoped to `secrets/git/`),
  i9 = OpenStack workloads incl. Jellyfin (media on a Cinder volume on the HDD), laptop = LLM.
- **k3s + Flux (GitOps)**, not Coolify. Coolify keeps config in its own DB/UI, which breaks single source of truth.
  Flux is what AKS GitOps uses. Plan for 3 small k3s VMs on OpenStack.
- **DNS on the Pi, outside the cluster** (AdGuard Home or Pi-hole), so core network services survive cluster or
  hypervisor downtime.
- **Single source of truth**: `inventory/network.yaml` (subnet, gateway, DHCP range, hosts/IPs/MACs), read by
  Terraform (`yamldecode`) and Ansible. No hardcoded IPs anywhere else.
- Secrets: sops + age (never plaintext in git).
- **age key in the workstation's TPM** (ADR-0015, amends ADR-0004): `age-plugin-tpm`, no PIN, so sops decrypts with
  no prompt; a backup age key lives only in the password manager. `.sops.yaml` uses the `age1tpm1…` recipient form.
- **Secrets in two layers** (ADR-0014): sops holds bootstrap secrets (OpenBao unseal keys, UniFi/OpenStack creds,
  restic password); OpenBao (Vault-compatible) holds runtime app secrets from step 5, fed to k3s by External
  Secrets Operator. Config stays in git; no App Configuration equivalent.
- **Private Forgejo on the fitlet2 is the source of truth** (ADR-0012); Copybara publishes a filtered copy to a
  public GitHub repo, with a gitleaks scan that blocks the push on any hit. A gitleaks pre-commit hook too.
  The fitlet2 runs nothing else core except OpenBao (ADR-0017), and not DNS.
- **Git server backups** (ADR-0013): nightly `forgejo dump` → restic to the fitlet2's microSD and to a second
  machine over SFTP; smartd watches the no-name SSD. The restic password is a second must-not-lose secret.
- **Ansible behind `make`** (ADR-0011): `ansible/inventory.py` generates the inventory from `network.yaml`,
  grouped by `role:` into `<role>_hosts` groups; settings in `ansible/group_vars/<role>_hosts.yml`; all versions pinned.
- **Runbooks** (ADR-0010): `docs/runbooks/<role>.md` per role, `docs/runbooks/common/` for cross-host procedures.
  Steps tagged [manual] / [script] / [check]. Runbooks are public, so placeholders only, no private values.
- **LLM host** (ADR-0009): bare-metal laptop, llama.cpp `llama-server` from the prebuilt Vulkan release
  (ROCm doesn't support Vega/gfx900), Open WebUI in Docker, Qwen 3.6 35B-A3B Q4_K_M, 64k context over 2 slots,
  q8_0 KV cache, `--n-cpu-moe` tuned. LAN-only ufw, API key. Ansible also disables lid/sleep and caps battery charge.
- UniFi Terraform provider is community-maintained. Verify coverage against my controller version and document gaps.

## Planned layout

```
inventory/network.yaml   source of truth
terraform/unifi/         networks, DHCP reservations, firewall, WLANs
openstack/               Kolla-Ansible config (globals.yml, inventory; passwords.yml sops-encrypted)
terraform/openstack/     networks, images, flavors, k3s instances
ansible/                 inventory.py, roles/<role>/, group_vars/<role>_hosts.yml
Makefile                 make llm / dns / git / openstack / all / ping
copy.bara.sky            Copybara: filtered export to the public GitHub mirror
.forgejo/workflows/      Forgejo Actions (Copybara sync + gitleaks)
clusters/                Flux manifests
secrets/                 sops-encrypted
docs/design.md, docs/decisions/ADR-*.md, docs/runbooks/
```

## Ideas backlog

`docs/ideas.md` collects future ideas. Whenever one comes up while we work (an alternative we deferred, a
consequence worth fixing later, a tool worth trying), add it there without being asked, under the right
heading, with what / why / when, and mention it in the reply. When an idea becomes an ADR or a roadmap step, move
it to "Done / promoted" with a link.

## Rollout (each step usable on its own; scope is a few weekends, then move on to DataFusion)

1. Repo, source of truth, secrets, local Terraform state
2. UniFi in Terraform (import existing config, don't recreate)
3. Pi DNS via Ansible, records generated from network.yaml
4. OpenStack on the i9 box (Kolla-Ansible), VMs as code
5. k3s + Flux, then move services in one at a time
6. DR test: wipe something on purpose, rebuild from the repo, measure the time

## Open questions to answer before starting

1. Which UniFi device runs the controller?
2. ~~What runs on the ESXi box today?~~ Pi-hole and Jellyfin VMs; both rebuilt from code, not migrated (2026-10-30).
3. ~~ESXi box CPU / RAM / storage~~ i9-12900HK, 64 GB, 2 TB NVMe + 1 TB HDD, 2 NICs (2026-10-30). Still needed:
   both NICs' interface names and MACs.
4. LLM host: real MAC, SSH username, confirm IP 192.168.10.30
5. fitlet2: confirm SSD; real MAC; confirm IP 192.168.10.3
6. Which machine holds the second (off-box) restic copy of the git server? (Candidate: the i9 box's HDD.)
9. Jellyfin: where is the old media now, how big is the library, and who watches it?
7. How many extra Pis, which models?
8. Back up Open WebUI chat history, or accept losing it on a rebuild?

## Next up (agreed 2026-10-30, not started)

Build with TODO placeholders where values are missing:
1. ~~`ansible/inventory.py` + `Makefile` (ADR-0011)~~ done
2. `llm` role: Vulkan llama.cpp, model download, systemd unit, Open WebUI, ufw, lid/sleep/battery (ADR-0009)
3. `git` role: Forgejo, Actions runner, restic + timers, smartd (ADR-0012, ADR-0013)
4. `copy.bara.sky` + sync workflow + gitleaks hook (ADR-0012)
5. `docs/runbooks/git.md` (including restoring from backup); drop the draft banners once scripts exist
