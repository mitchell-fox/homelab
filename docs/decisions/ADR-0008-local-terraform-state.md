# ADR-0008: Keep Terraform state local, then move it to self-hosted Postgres

- Status: Accepted
- Date: 2026-10-30
- Supersedes: [ADR-0002](ADR-0002-azure-state-backend.md)

## Context
ADR-0002 put Terraform state in Azure Storage. That conflicts with a hard constraint of this project:
everything runs offline, on my own hardware, at $0. Azure Storage is cheap, but it isn't free once the
12-month trial ends, and it makes every `terraform plan` depend on the internet and an Azure subscription.

State still needs to survive losing my laptop, and eventually it needs locking.

## Options
- **Local state file (gitignored)**: zero setup and works fully offline. No locking, and the file is lost if the laptop is.
- **`pg` backend on self-hosted Postgres**: built-in locking (Postgres advisory locks) on a database
  I'm learning anyway. It's the same engine as Azure Database for PostgreSQL, so the skills carry over to work.
- **S3 backend on MinIO**: works, but it's an S3 skill, not an Azure one, and it adds another service to run.
- **Azurite** (Microsoft's Azure Storage emulator): sounds ideal, but the azurerm backend is built for real
  Azure endpoints and authentication. Pointing it at an emulator isn't a supported setup.
- **Commit state to git, encrypted with sops**: no locking, merge conflicts on binary-ish JSON,
  and easy to forget to re-encrypt. Rejected.

## Decision
1. **Now:** local state per Terraform root (for example `terraform/unifi/terraform.tfstate`), gitignored.
2. **Later:** once Postgres runs on lab hardware outside anything Terraform manages (for example the Pi,
   which Ansible configures), switch to the `pg` backend with `terraform init -migrate-state`.

## Consequences
- Until step 2, losing the laptop loses the state. That's recoverable: the UniFi config can be re-imported,
  which is the same work as rollout step 2.
- The Postgres instance holding state must not be managed by the Terraform roots that use it. Otherwise
  rebuilding it would need the state it holds.
- The DR test (rollout step 6) covers restoring state from a backup.
