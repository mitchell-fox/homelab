# ADR-0002: Terraform state in Azure Storage

- Status: Accepted
- Date: 2026-10-30

## Context
Terraform state contains resource IDs and sometimes secrets. It needs locking, versioning, and a home
that survives the loss of any machine in the lab, including my laptop.

## Options
- **Local state**: simplest, but it's lost along with the laptop and has no locking.
- **State on a lab host (MinIO, or Postgres via the pg backend)**: circular. The lab would hold the state
  needed to rebuild the lab.
- **Terraform Cloud / HCP**: free tier works, but it's another account and doesn't build on my existing skills.
- **Azure Storage (azurerm backend)**: blob lease locking, soft delete and versioning, costs pennies a month,
  and ties directly to my Azure work. Key Vault can follow later.

## Decision
The azurerm backend in a dedicated storage account. The account is bootstrapped once with a small Bicep or
CLI script, because Terraform can't create its own backend.

## Consequences
- An internet connection and Azure credentials are needed to run `terraform plan`. That's acceptable for a lab.
- The bootstrap script is the one piece of chicken-and-egg infrastructure, and it is documented in `docs/`.
