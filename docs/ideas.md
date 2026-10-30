# Ideas backlog

Things to implement or consider later. Nothing here is decided. When an idea gets picked up, it becomes
an ADR (for a decision) or a roadmap step (for work), and the entry moves to **Done / promoted** with a link.

Each entry: what it is, why it's worth doing, and when it makes sense (the trigger or the rollout step it depends on).

## Infrastructure

- **Move Terraform state to the `pg` backend on self-hosted Postgres.**
  Why: survives losing the workstation, adds locking, and is Postgres practice (see ADR-0008).
  When: once Postgres runs somewhere Terraform doesn't manage, such as the Pi.
- **Run OpenBao on the fitlet2, next to Forgejo.**
  Why: ADR-0014 says OpenBao runs outside the cluster but names no host. The fitlet2 is always on, small, and
  already outside the cluster. Against it: ADR-0012 says the fitlet2 runs nothing else core, and the git server and
  the vault would share one no-name SSD. It would be the lab's vault, not its secret zero: rebuilding the fitlet2
  needs the restic password from sops, so the root key must stay off it (ADR-0015).
  Alternatives: a Pi, or a small VM outside k3s.
  Server-side key: give the fitlet2 its own age recipient (its TPM if it has one, else a plain key or a YubiKey 5),
  scoped in `.sops.yaml` to `secrets/git/` only (restic password, OpenBao unseal keys), so it can auto-unseal and
  self-restore without being able to decrypt UniFi/Proxmox creds. A YubiKey left plugged in needs touch disabled
  for unattended use, so it's barely better than a TPM there; it's more useful on a keychain as a portable
  recovery recipient. Check `ls /dev/tpm*` on the fitlet2.
  When: step 5, as an ADR that amends ADR-0012 or picks another host.
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

- Move the age key into the workstation's TPM → [ADR-0015](decisions/ADR-0015-age-key-in-tpm.md). Simplified to
  no PIN and a password-manager backup instead of paper; the remaining upgrades are listed above.
- Local git server (Forgejo) with a public GitHub mirror → [ADR-0012](decisions/ADR-0012-private-forgejo-public-mirror.md),
  backups in [ADR-0013](decisions/ADR-0013-git-server-backups.md). Mirror uses Copybara instead of a plain push mirror.
- OpenBao (Azure Key Vault equivalent) → [ADR-0014](decisions/ADR-0014-secrets-two-layers.md), built in step 5.
  Still open from the original idea: try OpenBao's Postgres storage backend and contributing to the project.
- Add the LLM host to `inventory/network.yaml` → done (host `llm`, [ADR-0009](decisions/ADR-0009-llm-host.md)).
