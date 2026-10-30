# ADR-0016: OpenStack on bare metal (Kolla-Ansible) on the i9 box, rebuilt from code instead of migrated

- Status: Accepted
- Date: 2026-10-30
- Supersedes: [ADR-0005](ADR-0005-proxmox-over-esxi.md)

## Context
ADR-0005 chose Proxmox to replace ESXi and planned to move the existing VMs with Proxmox's ESXi import wizard.
Two things changed before anything was installed:

- The ESXi box was wiped without exporting its two VMs (Pi-hole, Jellyfin). The import wizard pulls from a
  *running* ESXi host, so it was never going to work for an in-place replacement anyway.
- The goal shifted toward learning how a cloud works inside, not only running VMs. Azure keeps its control plane
  closed; an open-source cloud doesn't.

The box: Intel i9-12900HK (14 cores / 20 threads), 64 GB RAM, 2 TB NVMe, 1 TB SATA HDD, two NICs.
Because DNS, git and secrets live on other hardware ([ADR-0017](ADR-0017-host-roles.md)), this box only runs
workloads and experiments. It can be broken and rebuilt without taking the lab's core services with it.

## Options
- **Proxmox VE** (ADR-0005): mature bpg Terraform provider, web UI, ZFS, the largest homelab community.
  Teaches operating a hypervisor, not how a cloud works.
- **OpenStack, nested inside Proxmox**: keeps a stable base, but adds a virtualization layer and splits the RAM.
- **OpenStack on bare metal**: the full control plane (Keystone, Nova, Neutron/OVN, Cinder, Glance, Heat) on one
  node, deployed by Kolla-Ansible (OpenStack services as containers, deployed with Ansible).
- **Incus**: API-first, official Terraform provider, light. The runner-up if OpenStack proves too heavy.
- **XCP-ng + Xen Orchestra**: Xen is losing ground to KVM; Xen Orchestra is free only when built from source.
- **Plain Ubuntu + KVM/libvirt**: maximum Linux depth, but storage, networking and backups are all hand-built.
- **Harvester**: Kubernetes-native VMs, but wants 8+ cores and 32 GB+ per node and ideally 3 nodes.
- **Azure Local**: real on-prem Azure, but ~$10/physical core/month after a 60-day trial, needs an Azure
  subscription and a check-in every 30 days. Ruled out by the offline-and-free constraint.

## Decision
- **OpenStack on bare metal**, deployed by **Kolla-Ansible** from the workstation (the deploy host) with
  `make openstack`. Single-node "all-in-one" layout, HAProxy off. Kolla config lives in `openstack/`, with
  `passwords.yml` encrypted by sops. The Kolla-Ansible version is pinned (ADR-0011).
- **Host OS: Ubuntu Server 24.04 LTS**, the newest Ubuntu that Kolla-Ansible 2026.1 supports. The rest of the lab
  runs 26.04; this box moves to 26.04 when a Kolla release supports it, by reinstalling from code.
- **NIC 1 = management** (`network_interface`, static `192.168.10.10`). **NIC 2 = VM traffic**
  (`neutron_external_interface`, no IP; Neutron owns it). VMs reachable from the LAN get floating IPs from a range
  in `inventory/network.yaml`, outside the DHCP pool.
- **Everything above OpenStack is Terraform** (`terraform/openstack/`, the `openstack` provider): networks,
  security groups, images, flavors, and the 3 k3s instances ([ADR-0006](ADR-0006-k3s-flux-gitops.md)).
- **Rebuild, don't migrate.** Pi-hole becomes the Pi's DNS service ([ADR-0007](ADR-0007-dns-outside-cluster.md));
  Jellyfin is rebuilt on this box ([ADR-0017](ADR-0017-host-roles.md)).

## Consequences
- **Rollout step 4 becomes the hardest step.** Single-node Kolla deploys in an afternoon; debugging and the
  6-monthly upgrades are where the time goes. This competes with the plan to move on to DataFusion.
- **Fallback is cheap:** every workload on the box is defined in code, so switching to Proxmox or Incus later is a
  reinstall plus Terraform changes, not a migration.
- **Lost compared with Proxmox:** a click-through UI for quick fixes, one-click VM snapshots, simple GPU passthrough.
  GPU passthrough on OpenStack needs Nova PCI configuration.
- **Rebuilding the box is the step 6 DR test:** wipe, `make openstack`, `terraform apply`, Flux restores the apps.
- **Terraform credentials change** from a Proxmox API token to an OpenStack application credential, kept in sops.
- **The 1 TB HDD** backs Cinder volumes (media for Jellyfin, ADR-0017). Whether it also holds the git server's
  second backup copy is still open question 6.
