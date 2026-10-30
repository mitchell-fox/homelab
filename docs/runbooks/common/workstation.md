# Runbook: workstation

> **Status:** draft. The `make` targets referenced below are not built yet.

The workstation is whatever machine you run Ansible and Terraform from: today, the CachyOS desktop (Ryzen 9 5900XT,
RTX 5060 Ti; see `CLAUDE.md`). Not the LLM host, which is a laptop. It holds three things the repo can't:

| Item | Where | If lost |
|------|-------|---------|
| **age key (TPM-sealed)** | `~/.config/sops/age/keys.txt`, bound to this machine's TPM ([ADR-0015](../../decisions/ADR-0015-age-key-in-tpm.md)) | Recover with the backup age key from the password manager (section A). If both are lost, every secret is unreadable. |
| Terraform state | `terraform/*/terraform.tfstate` (gitignored, [ADR-0008](../../decisions/ADR-0008-local-terraform-state.md)) | Re-import the existing config (same work as rollout step 2) |
| SSH key | `~/.ssh/` | Re-add the new public key to every host by hand |

## A. Set up a fresh workstation

**When:** the workstation was reinstalled, or you're using a new one.
**Expected time:** ~10 min (longer if Terraform state has to be re-imported).

1. **[manual]** Install the tools:
   ```
   paru -S ansible terraform sops age age-plugin-tpm
   sudo usermod -aG tss $USER   # then log out and back in
   ```
2. **[manual]** Clone the repo:
   ```
   git clone <repo-url> ~/Projects/homelab
   ```
3. **[manual]** Give this machine its own TPM key and re-encrypt to it (the old TPM key can't move here):
   ```
   age-plugin-tpm --generate -o ~/.config/sops/age/keys.txt && chmod 600 ~/.config/sops/age/keys.txt
   age-plugin-tpm -y --tpm-recipient ~/.config/sops/age/keys.txt   # new recipient
   ```
   Replace the `age1tpm1…` recipient in `.sops.yaml` with the new one. Paste the backup key from the password
   manager into `/dev/shm/restore.txt`, then:
   ```
   SOPS_AGE_KEY_FILE=/dev/shm/restore.txt sops updatekeys -y secrets/*.sops.yaml
   shred -u /dev/shm/restore.txt
   ```
4. **[manual]** Restore your SSH key, or generate a new one and add it to each host's `authorized_keys`.
5. **[manual]** Restore Terraform state from backup, if you have one. If not, re-import it per ADR-0008.
6. **[check]** Secrets decrypt:
   ```
   sops -d secrets/llm.sops.yaml
   ```
7. **[check]** Ansible can reach every host:
   ```
   make ping
   ```

## Logs

| Date | Procedure | Time taken | Notes |
|------|-----------|------------|-------|
| | | | |
