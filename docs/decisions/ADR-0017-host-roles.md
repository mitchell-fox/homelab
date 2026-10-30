# ADR-0017: One job per box: Pi for DNS, fitlet2 for git and the vault, i9 for workloads

- Status: Accepted
- Date: 2026-10-30
- Amends: [ADR-0012](ADR-0012-private-forgejo-public-mirror.md) (the fitlet2 also runs OpenBao),
  [ADR-0014](ADR-0014-secrets-two-layers.md) (names OpenBao's host)

## Context
The lab has four always-on machines with very different strengths, and ADR-0014 said OpenBao runs "outside the
cluster" without naming a host. With the i9 box becoming an OpenStack box that will be broken and rebuilt often
([ADR-0016](ADR-0016-openstack-on-bare-metal.md)), the core services need homes that don't depend on it.

The rule behind ADR-0007, ADR-0012 and ADR-0014: **a service that's needed to rebuild something can't run on
the thing it rebuilds**, and core services shouldn't share a failure.

## Options
- **Everything core on the fitlet2** (DNS, git, vault): one fewer box to run, but one hardware failure takes out
  name resolution, the source of truth and the secrets at once.
- **The vault on the OpenStack box**: plenty of resources, but it breaks the rule above; OpenStack's own
  credentials would sit inside something OpenStack hosts.
- **One job per box** (below).

## Decision

| Box | Runs | Failure takes out |
|---|---|---|
| **Pi 4** (8 GB) | DNS (AdGuard Home or Pi-hole), as ADR-0007 decided | Name resolution; the router is the fallback |
| **fitlet2** (8 GB, 128 GB SSD, Ubuntu 26.04) | Forgejo + Actions runner, restic backups, **OpenBao** (step 5) | Git pushes and new secret reads; running services keep going |
| **i9 box** (64 GB, Ubuntu 24.04) | OpenStack → k3s VMs, Jellyfin, experiments | Workloads only; rebuilt from the repo |
| **LLM laptop** (64 GB, Ubuntu 26.04) | llama.cpp + Open WebUI (ADR-0009) | The LLM |

- **The fitlet2 runs git and the vault,** both "control plane" services needed to rebuild everything else. ADR-0012's
  rule becomes: the fitlet2 runs nothing else core, and specifically not DNS. Expected memory: Forgejo ~0.5 GB,
  OpenBao ~0.2 GB, the Actions runner up to ~1 GB during Copybara jobs. 8 GB leaves ample headroom.
- **The fitlet2 gets its own age recipient** (its TPM if it has one, else a plain key), scoped in `.sops.yaml` to
  `secrets/git/` only: the restic password and OpenBao's unseal keys. It can auto-unseal OpenBao and restore its
  own backups without being able to decrypt UniFi or OpenStack credentials. The workstation key and the
  password-manager backup key stay recipients of everything ([ADR-0015](ADR-0015-age-key-in-tpm.md)).
- **Jellyfin runs on the i9 box, inside OpenStack** (a k3s workload via Flux, or its own VM), with media on a Cinder
  volume backed by the 1 TB HDD. No transcoding at first, since most clients play the files directly. If needed
  later, pass the i9's iGPU through to a Jellyfin VM for Quick Sync.
- **The Pi and the fitlet2 run nothing experimental.**

## Consequences
- **The fitlet2 is now the most important machine**: losing it means losing git and the vault together. Its
  backups (ADR-0013) and the no-name SSD's health (smartd) matter more. Swapping in a known-brand SSD is worth it.
- **Auto-unseal trades security for convenience:** a stolen, running fitlet2 can open its own vault, the same
  trade as cloud auto-unseal. Acceptable for a homelab.
- **Jellyfin goes down whenever OpenStack does.** If others start depending on it, move it to the LLM laptop
  (Docker, Vega VAAPI transcoding), accepting that it shares 8 GB of VRAM with the LLM and needs an external drive.
- **Still open:** where the old Jellyfin media is and how big the library is (sizes the HDD's split), and which
  machine holds the git server's second backup copy (open question 6).
