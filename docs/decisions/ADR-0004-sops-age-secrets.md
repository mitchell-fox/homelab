# ADR-0004: Secrets encrypted with sops + age

- Status: Accepted
- Date: 2026-10-30

## Context
The repo is public. API tokens (UniFi, Proxmox), WiFi passphrases, and k3s tokens must still live
alongside the code they configure.

## Options
- **Keep secrets out of git** (a password manager plus manual steps): breaks "rebuild from the repo".
- **Ansible Vault**: only Ansible can read it.
- **Azure Key Vault from day one**: good, but it adds a dependency before anything works.
- **sops + age**: file-level encryption that keeps YAML keys readable, so diffs stay reviewable.
  Terraform (carlpett/sops provider), Ansible (community.sops), and Flux all decrypt it natively.

## Decision
sops with age keys. The private key lives outside the repo, backed up in a password manager.

## Consequences
- Losing the age private key means losing every secret, so key backup is part of the DR test (step 6).
- Key Vault can become a sops key source later without re-architecting.
