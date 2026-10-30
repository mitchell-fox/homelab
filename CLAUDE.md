# Homelab as code

Rebuild and codify my home network. Spectrum swapped my equipment, which forced a subnet change from
192.168.1.0/24 to 192.168.10.0/24. The goal: the next change like that is a one-line diff.
It's also meant to be an interview talking point, so design decisions get written down as ADRs.

## Hardware

- UniFi router (exact model / where the controller runs: TBD)
- ESXi box, which I'm migrating to Proxmox (current VMs and specs: TBD)
- Raspberry Pi 4, 8 GB

## Decisions so far

- **Terraform** (not OpenTofu): same HCL, and matches job listings. Bicep can't manage UniFi or Proxmox.
- **Terraform state in Azure Storage** (azurerm backend). This ties the lab to my Azure work; Key Vault later.
- **Proxmox over ESXi**: free ESXi restricts the write API; Proxmox has the bpg/proxmox provider, cloud-init,
  and a built-in ESXi import wizard.
- **k3s + Flux (GitOps)**, not Coolify. Coolify keeps config in its own DB/UI, which breaks single source of truth.
  Flux is what AKS GitOps uses. Plan for 3 small k3s VMs on Proxmox.
- **DNS on the Pi, outside the cluster** (AdGuard Home or Pi-hole), so core network services survive cluster or
  hypervisor downtime.
- **Single source of truth**: `inventory/network.yaml` (subnet, gateway, DHCP range, hosts/IPs/MACs), read by
  Terraform (`yamldecode`) and Ansible. No hardcoded IPs anywhere else.
- Secrets: sops + age (never plaintext in git).
- UniFi Terraform provider is community-maintained. Verify coverage against my controller version and document gaps.

## Planned layout

```
inventory/network.yaml   source of truth
terraform/unifi/         networks, DHCP reservations, firewall, WLANs
terraform/proxmox/       VMs from cloud-init templates
ansible/                 Pi DNS, k3s bootstrap
clusters/                Flux manifests
secrets/                 sops-encrypted
docs/design.md, docs/decisions/ADR-*.md
```

## Rollout (each step usable on its own; scope is a few weekends, then move on to DataFusion)

1. Repo, source of truth, secrets, Azure state backend
2. UniFi in Terraform (import existing config, don't recreate)
3. Pi DNS via Ansible, records generated from network.yaml
4. Proxmox migration, VMs as code
5. k3s + Flux, then move services in one at a time
6. DR test: wipe something on purpose, rebuild from the repo, measure the time

## Open questions to answer before starting

1. Which UniFi device runs the controller?
2. What runs on the ESXi box today?
3. ESXi box CPU / RAM / storage (to size 3 k3s VMs)
