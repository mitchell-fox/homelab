# ADR-0014: Secrets in two layers (sops for bootstrap, OpenBao at runtime); config stays in git

- Status: Accepted (the OpenBao layer is built in rollout step 5)
- Date: 2026-10-30
- Builds on: [ADR-0004](ADR-0004-sops-age-secrets.md)

## Context
At work, secrets live in Azure Key Vault and runtime config in Azure App Configuration. Using the same model
here builds skills that carry over. But this lab must be able to rebuild itself from nothing, offline.

## Options
- **sops only**: no running service, so it decrypts offline on the worst day. But it has no access policies,
  audit log, dynamic secrets, or rotation, and it's less like Key Vault.
- **OpenBao only** (the open-source fork of Vault, same API and CLI): close to Key Vault. But it's a service that
  has to be running and unsealed before anything can read from it. If it runs in the lab, rebuilding the lab
  needs a vault the lab hosts.
- **Both, in layers**: sops holds only what's needed to bring the vault up. OpenBao holds everything apps use
  while running. This is the common industry split.
- **A config service (the App Configuration equivalent, such as Consul KV)**: in GitOps, git already *is* the
  config store, with history and review. A separate service would put config outside git, which is the reason
  Coolify was rejected (ADR-0006).

## Decision
- **Bootstrap layer: sops + age, in git.** It holds:
  - OpenBao's unseal keys.
  - The credentials Ansible and Terraform need for core hosts (UniFi, Proxmox).
  - The restic password.
- **Runtime layer: OpenBao,** added in step 5 and run outside the cluster. It holds app secrets: the LLM API key,
  database passwords, service credentials. k3s reads them through External Secrets Operator, the same pattern as
  AKS with Key Vault.
- **Config stays in git:** `inventory/network.yaml`, `group_vars`, and Flux manifests. No config service.

## Consequences
- **Until step 5,** everything is in sops, and the LLM API key moves to OpenBao then.
- **OpenBao needs unsealing after every restart.** Auto-unseal normally relies on a cloud KMS, which this
  lab rules out, so it starts as manual unseal from keys kept in sops and the password manager.
  The runbook covers it.
- **OpenBao is another core service that must be outside what it serves,** with its own backups.
- The age key is still the root of trust. The idea to bind it to the workstation's TPM (`docs/ideas.md`) still applies.
