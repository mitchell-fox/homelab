# ADR-0013: Git server backups with restic, to the local microSD and a second machine

- Status: Accepted
- Date: 2026-10-30

## Context
The fitlet2 running Forgejo ([ADR-0012](ADR-0012-private-forgejo-public-mirror.md)) has a no-name SATA SSD.
Every rebuild depends on this box, so losing its data is the worst failure in the lab.
The fitlet2 has a microSD slot.

## Options
- **Image the whole SSD to the SD card (`dd`)**: copying a live disk gives an inconsistent image, and
  rewriting the full disk every night wears out the SD card.
- **Copy `forgejo dump` output with `cp` or `rsync`**: no encryption, no history, so a corrupted repo
  overwrites the good copy.
- **restic**: encrypted, deduplicated, versioned snapshots with retention rules, and multiple destinations.
  Free and offline.

## Decision
- **Snapshot:** `forgejo dump` runs nightly from a systemd timer. It's a consistent snapshot of the repos,
  database, and config.
- **Store:** restic backs the dump up to two places:
  1. **The microSD card in the fitlet2,** mounted by UUID with `nofail`. Use a name-brand High Endurance card.
     This covers the SSD dying.
  2. **A second machine over SFTP** (which one is still open). This covers the whole fitlet2 dying.
- **Retention:** keep 7 daily, 4 weekly, and 6 monthly snapshots.
- **Early warning:** `smartd` monitors the SSD for signs of failure.
- **Restore test:** the git-server runbook includes a restore procedure, and the DR test (step 6) runs it.

## Consequences
- **The restic password is a second must-not-lose secret,** alongside the age key. It's kept in the password
  manager, and deployed to the box from sops.
- **Not covered:** fire, theft, or a surge that takes out every machine. There's no off-site copy, by choice;
  this is a $0, offline lab.
- **The SD card is not reliable storage either.** It's one of two copies, not the only one.
