# Secrets

Only sops-encrypted files go here (ADR-0004). Name them `*.sops.yaml` so `.sops.yaml` at the repo root
encrypts them automatically with the age recipients it lists.

```sh
sops edit secrets/<name>.sops.yaml     # create or edit; decrypts to a temp file, re-encrypts on save
sops decrypt secrets/<name>.sops.yaml  # print plaintext to stdout
```

Never write a plaintext file here and encrypt it afterwards; `sops edit` keeps plaintext off disk in the repo.

## The age key

Every file is encrypted to two recipients ([ADR-0015](../docs/decisions/ADR-0015-age-key-in-tpm.md)):

- **workstation-tpm**: `~/.config/sops/age/keys.txt` is a TPM-sealed identity, useless on any other machine.
  sops finds it automatically and decrypts without a prompt (needs `age-plugin-tpm` and membership in `tss`).
- **backup**: a plain age key that lives only in the password manager. Use it when the TPM key is gone:
  ```sh
  # paste the key from the password manager into /dev/shm/restore.txt (RAM, not disk)
  SOPS_AGE_KEY_FILE=/dev/shm/restore.txt sops decrypt secrets/<name>.sops.yaml
  shred -u /dev/shm/restore.txt
  ```
  If both keys are lost, every file in this folder is unreadable.
- Adding a recipient (a backup key, or a key for Flux later): add its public key to `.sops.yaml`, then
  run `sops updatekeys secrets/*.sops.yaml` to re-encrypt existing files.
