# Ideas backlog

Things to implement or consider later. Nothing here is decided. When an idea gets picked up, it becomes
an ADR (for a decision) or a roadmap step (for work), and the entry moves to **Done / promoted** with a link.

Each entry: what it is, why it's worth doing, and when it makes sense (the trigger or the rollout step it depends on).

## Infrastructure

- **Move Terraform state to the `pg` backend on self-hosted Postgres.**
  Why: survives losing the workstation, adds locking, and is Postgres practice (see ADR-0008).
  When: once Postgres runs somewhere Terraform doesn't manage, such as the Pi.
- **Move the i9 box to Ubuntu 26.04 once Kolla-Ansible supports it.**
  Why: Kolla-Ansible 2026.1 supports Ubuntu 24.04 only, so the i9 box is the one host on an older Ubuntu (ADR-0016).
  How: reinstall and redeploy from the repo, timed, which doubles as the step 6 DR test.
  When: when a Kolla release lists Ubuntu 26.04 in its support matrix.
- **GPU passthrough of the i9's iGPU to a Jellyfin VM (Nova PCI passthrough) for Quick Sync transcoding.**
  Why: ADR-0017 starts Jellyfin without transcoding. When: only if a client can't play files directly.
- **Used 1-liter mini PCs (Lenovo M720q / Dell OptiPlex Micro / HP EliteDesk Mini) as extra OpenStack compute / k3s nodes.**
  Why: old phones were considered and rejected: they can't run Proxmox, need custom kernels for containers, are
  Wi-Fi only, and their batteries swell when left on a charger 24/7. A used 8th/9th-gen i5 mini PC (~$90–200 on eBay)
  has x86, NVMe, gigabit Ethernet and 16–64 GB RAM, and idles around 10 W.
  When: if the ESXi box can't fit 3 k3s VMs (open question 3), or for a real multi-node cluster in step 5/6.
- **Old iPhone 8 Plus as a wall-mounted Grafana / status dashboard.**
  Why: a realistic use for a phone in the lab: a read-only screen, no jailbreak, no server duties.
  Use Guided Access to lock it to one page, and put the charger on a smart plug timer to protect the battery (the 8 Plus has no hard 80% charge limit).
  When: after Prometheus + Grafana exist.

- **Prometheus + Grafana** (Azure Monitor managed Prometheus/Grafana): cluster and host monitoring. After step 5.
- **Keycloak or Authentik** (Entra ID): single sign-on via OIDC for lab services. After a few services exist.
- **Harbor** (Azure Container Registry): a local image registry, which also helps the cluster stay offline.
- **Azurite** (Azure Storage emulator): local blob, queue and table storage for apps I write.

- **Azure Local (formerly Azure Stack HCI), 60-day trial.** Why: the real on-prem Azure, managed via Arc. Not for
  the lab: ~$10/physical core/month after the trial, needs an Azure subscription and a check-in at least every
  30 days, and has strict hardware requirements. It teaches operating Azure, not its internals.
  When: only as a time-boxed experiment on spare hardware, if work starts using it.

## Networking

- **Sandbox VLAN: internet access only, no route to anything internal.**
  Why: a place for untrusted devices, software and experiments that can't reach the rest of the lab.
  Needs its own firewall zone that blocks all internal zones, the router's management, and private address ranges
  on the upstream side (the Spectrum equipment), allowing only DHCP from the router, plus DNS if the router serves it.
  When: with the UniFi zone setup; the working list of networks is in `~/homelab/network.md` (outside this repo), so
  record the final list in an ADR and `network.yaml`.

- **Small managed UniFi switch for per-port VLANs.**
  Why: the UCG Ultra has only 4 LAN ports, and the Pi, fitlet2, the i9's two NICs and the LLM laptop need five wired
  connections. One managed switch sets each port's network in software, over a single tagged uplink.
  When: when the lab machines run out of gateway ports, likely once the fitlet2 and i9 move to the Servers VLAN.

- **Slim the DNS Pi down to a server install.**
  Why: it runs Raspberry Pi OS with the desktop, plus printing, VNC, NFS and Bluetooth services a DNS box doesn't
  need. Fewer services means less to patch, less exposed on the network, and a closer match to ADR-0017's one job per box.
  When: after Pi-hole is stable; removing packages or reinstalling from the Ansible role both work, and the
  reinstall doubles as a rebuild test.

- **One `network.yaml` entry per VLAN, with hosts assigned to a network.**
  Why: the file models only the Default network, while UniFi now has VLANs 10, 20, 30 and 40, so those live only in
  `~/homelab/network.md`. When: before managing UniFi with Terraform, or when a host moves to Servers.
- **Generate Pi-hole local DNS records from `network.yaml`.**
  Why: ADR-0007 wants `<host>.home.arpa` names generated from the source of truth; `make dns` doesn't do this yet.
  When: once the planned hosts' IPs are confirmed, so no names point at the wrong place.
- **Unbound as Pi-hole's upstream, replacing Quad9.**
  Why: resolves names itself instead of trusting one outside provider, which fits the self-hosted goal. It gives up
  Quad9's malware blocking (HaGeZi's Threat Intelligence Feeds partly cover that), and lookups are still unencrypted.
  Needs DNSSEC handling for a Pi with no battery-backed clock. When: after Pi-hole has run on Quad9 for a few days.
- **Monitoring, alerting and health checks for Pi-hole.**
  Why: DNS is now a whole-house dependency that updates itself overnight, and a failed update, list refresh or
  rollback is silent today. Check that it answers, blocks and is fresh, watch the timers and SD card, and send an alert.
  When: soon; with Prometheus + Grafana, or a small check script before they exist.
- **Second DNS server for when the Pi is down.**
  Why: a second Pi-hole would remove the single point of failure without letting ads through, which a router
  fallback would (clients can use either server). When: if a Pi outage actually hurts, or a spare Pi is free.
- **Back up Pi-hole allowlists made in the web UI, or manage them in the repo.**
  Why: `make dns` restores settings and blocklists, but not allowlist entries. Teleporter exports them.
  When: once a few allowlist entries exist.
- **Add StevenBlack's hosts list to Pi-hole.**
  Why: measured 2026-11-01, it adds about 21,000 hostnames beyond HaGeZi Pro++ and the Threat Intelligence Feeds, and
  about 39% of a 400-domain sample still resolved. It also blocks some affiliate and site-testing domains they don't.
  When: only if the query log shows ads still coming through domains it covers.

## LLM host

- **Ubuntu autoinstall for hands-off rebuilds.**
  Why: removes the ~15 min manual install from the LLM runbook's rebuild procedure (and other Ubuntu hosts).
  When: after the DR test shows the manual install is the slow part; not before.
- **llama-swap in front of llama-server.**
  Why: serve several models (a small fast one plus the 35B) and load them on demand.
  When: once one model is running well and there's a real need for a second.

## Quality and tooling

- **JSON Schema for `network.yaml`, validated in CI or a pre-commit hook.**
  Why: the schema is informal (ADR-0003); a typo in an IP or MAC should fail fast.
- **Compute host IPs with `cidrhost()` offsets instead of literal IPs.**
  Why: makes a renumbering a true one-line change (ADR-0003 consequences). Weigh against readability.
- **Pre-commit hook that rejects unencrypted files in `secrets/`.**
  Why: one `git add` of a plaintext file in a public repo leaks it for good. Check for the `sops:` metadata key.
  When: soon; cheap insurance before real secrets land.
- **Harden the TPM age key: PIN, Shamir-split backup, FIDO2 recipient, or a YubiKey as the admin key.**
  Why: ADR-0015 chose no PIN and a single password-manager backup for low friction. With no PIN, an unencrypted
  disk, and no PCR binding, a stolen powered-off workstation can boot a live USB and use the TPM key. A PIN
  (`--pin`, TPM anti-hammering makes a short one safe) closes that and stops someone at an unlocked session.
  Stronger: make a YubiKey 5 (`age-plugin-yubikey`, touch policy `cached`) the admin key, so malware can't decrypt
  without a physical touch, and keep the TPM key only if the friction is too much. Splitting the backup 2-of-3 with `age-plugin-sss` is practice for OpenBao's unseal model; a
  cheap FIDO2 key (`age-plugin-fido2-hmac`) is a portable recipient that survives the workstation dying.
  When: if the password manager starts to feel like too big a single point of failure, or as OpenBao prep (step 5).
- **Switch the TPM recipient to `age1tag1…` once `age-plugin-tag` is packaged.**
  Why: `age-plugin-tpm` now defaults to the p256tag recipient, but sops needs an `age-plugin-tag` binary for it,
  which Arch's `age` 1.3.2 doesn't ship, so ADR-0015 uses the old `age1tpm1…` form.
  When: if `age-plugin-tpm` drops the old-style recipient, or Arch starts shipping `age-plugin-tag`.
- **Full-disk encryption on the workstation (LUKS, unlocked by TPM + PIN via `systemd-cryptenroll`).**
  Why: the disk is unencrypted today, so SSH keys, Terraform state, and anything else on it is readable from a
  stolen workstation. The TPM-bound age key fixes secrets only.
  When: at the next reinstall; encrypting an existing root in place is possible but risky, and snapper
  snapshots live on the same disk, so they're no safety net for it. Plan it as a reinstall plus restore.
- **Hand out the router as secondary DNS via DHCP.**
  Why: the Pi is a single point of failure for DNS (ADR-0007). Do it in step 3.

## Done / promoted

- OpenStack as the lab's platform, on bare metal instead of nested → [ADR-0016](decisions/ADR-0016-openstack-on-bare-metal.md),
  which also records the wider hypervisor comparison (Incus, XCP-ng, libvirt, Harvester, Azure Local).
- OpenBao on the fitlet2 with its own scoped age key, and Jellyfin's placement → [ADR-0017](decisions/ADR-0017-host-roles.md).
- Move the age key into the workstation's TPM → [ADR-0015](decisions/ADR-0015-age-key-in-tpm.md). Simplified to
  no PIN and a password-manager backup instead of paper; the remaining upgrades are listed above.
- Local git server (Forgejo) with a public GitHub mirror → [ADR-0012](decisions/ADR-0012-private-forgejo-public-mirror.md),
  backups in [ADR-0013](decisions/ADR-0013-git-server-backups.md). Mirror uses Copybara instead of a plain push mirror.
- OpenBao (Azure Key Vault equivalent) → [ADR-0014](decisions/ADR-0014-secrets-two-layers.md), built in step 5.
  Still open from the original idea: try OpenBao's Postgres storage backend and contributing to the project.
- Add the LLM host to `inventory/network.yaml` → done (host `llm`, [ADR-0009](decisions/ADR-0009-llm-host.md)).
