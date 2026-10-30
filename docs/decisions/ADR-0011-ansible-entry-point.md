# ADR-0011: `make` targets over Ansible, with the inventory generated from `network.yaml`

- Status: Accepted
- Date: 2026-10-30

## Context
Rebuilding a host should be one command that's easy to remember, and running it twice should be safe.
Ansible needs an inventory (which hosts, at which IPs), but ADR-0003 forbids IPs anywhere except
`inventory/network.yaml`.

## Options
- **Static Ansible inventory file**: a second copy of every IP, which ADR-0003 rules out.
- **Inventory script reading `network.yaml`**: one source of truth. Groups come from each host's `role:`.
- **Raw `ansible-playbook` commands in the runbooks**: long, easy to get wrong under pressure.
- **`make` targets wrapping them**: short, easy to find (`make help`), and the runbooks only ever say `make <target>`.

## Decision
- **Inventory:** `ansible/inventory.py` reads `inventory/network.yaml` and groups hosts by `role:`.
  Each group's settings live in `ansible/group_vars/<role>.yml`.
- **Entry point:** a top-level `Makefile`, with targets such as `make llm`, `make dns`, `make all`, and `make ping`.
- **Playbooks are idempotent.** Rebuilds, updates, and config changes all use the same command.
- **Everything is pinned:** llama.cpp, container images, model files (by checksum), and collection versions.
  A rebuild must produce the same result as last time.

## Consequences
- A new host is one entry in `network.yaml` plus a role. The inventory picks it up automatically.
- Target hosts need only SSH and Python, both present on a fresh Ubuntu Server install.
- Upgrades become deliberate version bumps in git, which the runbooks record (procedure "Routine update").
