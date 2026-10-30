# Secrets

Only sops-encrypted files go here (ADR-0004). Name them `*.sops.yaml` so `.sops.yaml` at the repo root
encrypts them automatically with the age recipients it lists.

```sh
sops edit secrets/<name>.sops.yaml     # create or edit; decrypts to a temp file, re-encrypts on save
sops decrypt secrets/<name>.sops.yaml  # print plaintext to stdout
```

Never write a plaintext file here and encrypt it afterwards; `sops edit` keeps plaintext off disk in the repo.

## The age key

- Private key: `~/.config/sops/age/keys.txt` (sops finds it there automatically). **Not in this repo.**
- Back it up to your password manager. If it's lost, every file in this folder is unreadable.
- Adding a recipient (a backup key, or a key for Flux later): add its public key to `.sops.yaml`, then
  run `sops updatekeys secrets/*.sops.yaml` to re-encrypt existing files.
