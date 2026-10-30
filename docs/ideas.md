# Ideas backlog

Things to implement or consider later. Nothing here is decided. When an idea gets picked up, it becomes
an ADR (for a decision) or a roadmap step (for work), and the entry moves to **Done / promoted** with a link.

Each entry: what it is, why it's worth doing, and when it makes sense (the trigger or the rollout step it depends on).

## Infrastructure

- **Move Terraform state to the `pg` backend on self-hosted Postgres.**
  Why: survives losing the workstation, adds locking, and is Postgres practice (see ADR-0008).
  When: once Postgres runs somewhere Terraform doesn't manage, such as the Pi.
- **Used 1-liter mini PCs (Lenovo M720q / Dell OptiPlex Micro / HP EliteDesk Mini) as extra Proxmox/k3s nodes.**
  Why: old phones were considered and rejected: they can't run Proxmox, need custom kernels for containers, are
  Wi-Fi only, and their batteries swell when left on a charger 24/7. A used 8th/9th-gen i5 mini PC (~$90–200 on eBay)
  has x86, NVMe, gigabit Ethernet and 16–64 GB RAM, and idles around 10 W.
  When: if the ESXi box can't fit 3 k3s VMs (open question 3), or for a real multi-node cluster in step 5/6.
- **Old iPhone 8 Plus as a wall-mounted Grafana / status dashboard.**
  Why: a realistic use for a phone in the lab: a read-only screen, no jailbreak, no server duties.
  Use Guided Access to lock it to one page, and put the charger on a smart plug timer to protect the battery (the 8 Plus has no hard 80% charge limit).
  When: after Prometheus + Grafana exist.

## Azure-equivalent tools (for upskilling)

- **Prometheus + Grafana** (Azure Monitor managed Prometheus/Grafana): cluster and host monitoring. After step 5.
- **Keycloak or Authentik** (Entra ID): single sign-on via OIDC for lab services. After a few services exist.
- **Harbor** (Azure Container Registry): a local image registry, which also helps the cluster stay offline.
- **Azurite** (Azure Storage emulator): local blob, queue and table storage for apps I write.

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
- **Move the age key into the workstation's TPM (`age-plugin-tpm`), with an offline paper backup recipient.**
  Why: today `keys.txt` is a plain file on an unencrypted disk, so anyone with the workstation or a copy of the disk
  can decrypt every secret. A TPM-bound key can't be copied off the workstation. Free: the workstation has TPM 2.0, the
  plugin is in `extra`, and sops supports age plugins (3.10+).
  Design: `.sops.yaml` lists recipients `workstation-tpm` (daily use), `backup-paper` (a plain age key, printed, kept
  offline; never on disk), and later `flux` (step 5, a software key as a Kubernetes Secret, since a cluster can't
  reach the workstation's TPM). Losing the workstation, a motherboard swap, or a TPM clear (some BIOS updates reset a
  firmware TPM) kills the TPM key, so the paper backup is required, not optional.
  Optional upgrades: split the paper key 2-of-3 with Shamir (`age-plugin-sss`) for practice with OpenBao's unseal
  model; add a cheap FIDO2 key (`age-plugin-fido2-hmac`, works with any key that supports `hmac-secret`) as a
  portable recipient that survives the workstation dying.
  When: now, before any real secrets land in `secrets/`. Write it up as an ADR that amends ADR-0004.
  Background in [reading.md](reading.md).
- **Full-disk encryption on the workstation (LUKS, unlocked by TPM + PIN via `systemd-cryptenroll`).**
  Why: the disk is unencrypted today, so SSH keys, Terraform state, and anything else on it is readable from a
  stolen workstation. The TPM-bound age key fixes secrets only.
  When: at the next reinstall; encrypting an existing root in place is possible but risky, and snapper
  snapshots live on the same disk, so they're no safety net for it. Plan it as a reinstall plus restore.
- **Hand out the router as secondary DNS via DHCP.**
  Why: the Pi is a single point of failure for DNS (ADR-0007). Do it in step 3.

## Done / promoted

- Local git server (Forgejo) with a public GitHub mirror → [ADR-0012](decisions/ADR-0012-private-forgejo-public-mirror.md),
  backups in [ADR-0013](decisions/ADR-0013-git-server-backups.md). Mirror uses Copybara instead of a plain push mirror.
- OpenBao (Azure Key Vault equivalent) → [ADR-0014](decisions/ADR-0014-secrets-two-layers.md), built in step 5.
  Still open from the original idea: try OpenBao's Postgres storage backend and contributing to the project.
- Add the LLM host to `inventory/network.yaml` → done (host `llm`, [ADR-0009](decisions/ADR-0009-llm-host.md)).
