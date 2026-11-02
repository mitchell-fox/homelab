# ADR-0012: Private Forgejo as source of truth, public GitHub mirror via Copybara

- Status: Accepted
- Date: 2026-10-30
- Amends: [ADR-0004](ADR-0004-sops-age-secrets.md) (its context assumes the only repo is public)

## Context
The repo is portfolio material, so it should be public. But some values (MACs, usernames, operational details)
are better kept private, and Flux pulling from GitHub would make deploys depend on the internet, which breaks
the offline constraint.

A pattern from industry: an internal repo is the source of truth, and an automated job publishes a filtered
copy. Google built Copybara for this.

## Options
- **Public repo only, with sops field-level encryption** (`encrypted_regex` for MACs): simple, but every
  private value must be encrypted, and deploys still need GitHub.
- **Private repo only**: safe, but no portfolio value.
- **A sanitized copy of `network.yaml` kept separately**: two files to keep in sync, which breaks ADR-0003.
- **Private Forgejo plus a `git filter-repo` script** that drops excluded paths and pushes: works, but it can only
  remove whole files, not scrub values inside a file, and GitHub stays one-way.
- **Private Forgejo plus Copybara**: excludes files and rewrites content (`core.replace` can scrub MACs inside
  `network.yaml`, so the source of truth stays one file). It can also import GitHub pull requests back.
  It's also a tool worth learning.

## Decision
- **Forgejo on the fitlet2** is the source of truth. Forgejo Actions handles CI, using the GitHub Actions
  syntax, which carries over to GitHub Actions and is close to Azure Pipelines.
- **The fitlet2 runs nothing else core**, and specifically not DNS, so one hardware failure can't take out both.
  It is outside the cluster and hypervisor it helps rebuild.
- **Copybara (`copy.bara.sky`)** runs in Forgejo Actions on every push to `main`:
  1. Export with excluded paths dropped and private values scrubbed.
  2. **Run gitleaks on the result. Any hit aborts the push.**
  3. Push to GitHub.
- **A gitleaks pre-commit hook** on the workstation catches leaks before they reach Forgejo.
- **sops stays.** Secrets are encrypted even in the private repo (defense in depth: backups, disk images,
  an exposed Forgejo).
- **The public README states it's a mirror.** Contributions are imported through Copybara, not merged on GitHub.

## Consequences
- **The git server becomes the most critical machine.** Every rebuild starts by cloning from it.
  Backups are covered in [ADR-0013](ADR-0013-git-server-backups.md).
- **Exclusions only work if private values stay where the rules expect them.** A secret pasted into an
  unexpected file is caught by gitleaks, not by Copybara.
- **The GitHub copy is not a backup**, since it lacks exactly the private parts a rebuild needs.
- **Copybara is a Java program, configured in Starlark.** The fitlet2 needs a JDK, and there's new
  syntax to learn.
- **Flux (step 5) pulls from Forgejo,** so deploys work offline.
