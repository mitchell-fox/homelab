# ADR-0010: Runbooks per role, with shared procedures in `common/`

- Status: Accepted
- Date: 2026-10-30

## Context
ADRs explain why things are built a certain way. Scripts explain how, to a machine. A person rebuilding a host
under pressure needs a third thing: the order of steps, which ones are manual, which are one command, and how
to check each one worked. More hosts are coming (DNS Pi, git server, Proxmox, k3s), so the layout has to scale.

## Options
- **One folder per host**: easy to find a host's runbook, but hosts get renamed and replaced, the three k3s VMs
  would need three copies, and procedures that span hosts (workstation setup, renumbering) belong to none of them.
- **One big runbook**: becomes unreadable quickly.
- **One file per role, plus `common/` for procedures that span roles**: the file name matches `role:` in
  `network.yaml` and the Ansible role, so the inventory, the automation, and the runbook all line up.

## Decision
`docs/runbooks/<role>.md` for each role, `docs/runbooks/common/` for procedures that span roles.
A role becomes a folder (`<role>/README.md`) only when it outgrows one file.

Every step is tagged **[manual]**, **[script]** (one `make` command), or **[check]**.

Every role runbook includes:

- A table of what the repo restores and what it doesn't.
- The procedures, each finishing with the health check.
- A troubleshooting table.
- A log of real runs with the time taken.

Conventions are in `docs/runbooks/README.md`.

## Consequences
- Runbooks are public portfolio material, so they never contain private values. Placeholders only.
- Steps written before their scripts exist must be marked as drafts until the scripts are built.
- Run logs give the DR test (step 6) real numbers instead of guesses.
- A wrong runbook step is fixed in the same commit as the recovery that exposed it.
