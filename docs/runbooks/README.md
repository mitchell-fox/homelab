# Runbooks

ADRs explain *why* things are built the way they are. Runbooks explain *what to do*, step by step,
for a person at a keyboard.

## Layout

```
runbooks/
  README.md          this file: conventions and index
  common/            procedures that span hosts (workstation setup, renumbering, DR test)
  <role>.md          one runbook per role in inventory/network.yaml (llm.md, dns.md, k3s.md, ...)
```

- **One runbook per role, not per host.** The three k3s VMs share `k3s.md`. Hosts get replaced and renamed;
  roles stay. The file name matches `role:` in `network.yaml` and the Ansible role, so all three line up.
- **Shared procedures go in `common/`.** If a procedure touches more than one role, it lives there,
  and each role runbook links to it instead of repeating it.
- **Promote a role to a folder only when it outgrows one file.** If you do, use `<role>/README.md`
  so existing links still make sense.

## Conventions

Every step is tagged with who does it:

- **[manual]**: you do it by hand (installer screens, plugging things in, the UniFi UI).
- **[script]**: one command from the repo. The runbook gives the exact command; the script does the work.
- **[check]**: a verification. Don't move on until it passes.

Each procedure lists:

- When to run it.
- Prerequisites.
- Steps.
- How long it should take.

Each role runbook ends with a health check that every other procedure finishes with.
After running a procedure, add a row to that runbook's log table so the times reflect real runs, not guesses.

If a step is wrong, fix the runbook in the same commit as whatever you changed to recover.

To add a role runbook, copy the structure of [llm.md](llm.md):

- Summary table.
- What is and isn't restored.
- Procedures.
- Health check.
- Troubleshooting.
- Logs.

## Index

| Runbook | Covers | Status |
|---------|--------|--------|
| [common/workstation](common/workstation.md) | Setting up the machine you run Ansible and Terraform from | Draft |
| [common/renumber](common/renumber.md) | Subnet, IP, or NIC changes across the network | Draft |
| [llm](llm.md) | Local LLM server: llama.cpp, Open WebUI, model, API access | Draft |
| git | Private Forgejo on the fitlet2, Copybara mirror, restic backups and restore | Not written |
| [dns](dns.md) | Pi DNS: Pi-hole, blocklists, pointing networks at it | Current |
| hypervisor | OpenStack on the i9 box: Kolla deploy, upgrade, rebuild (rollout step 4) | Not written |
| k3s | Cluster and Flux (rollout step 5) | Not written |
| common/dr-test | Wipe and rebuild on purpose, measure the time (rollout step 6) | Not written |
