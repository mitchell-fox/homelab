# ADR-0015: The workstation's age key lives in its TPM, with a password-manager backup key

- Status: Accepted
- Date: 2026-10-30
- Amends: [ADR-0004](ADR-0004-sops-age-secrets.md)

## Context
ADR-0004 left the age private key as a plain file (`~/.config/sops/age/keys.txt`) on the workstation's unencrypted
disk. Anyone with the workstation, a copy of its disk, or a backup of the home directory could decrypt every secret.
The workstation has TPM 2.0, and sops supports age plugins.

## Options
- **Plain key file (status quo):** zero friction, but the key can be copied.
- **Passphrase-encrypted age key:** can still be copied, and you type the passphrase on every decrypt.
- **TPM-bound key (`age-plugin-tpm`), no PIN:** the key can't leave this TPM, and decrypts need no prompt.
- **TPM-bound key with a PIN:** also stops someone at an unlocked session, but you type the PIN on every decrypt.
- **Hardware token (YubiKey / FIDO2):** portable, but it costs money and needs a touch on every decrypt.

## Decision
- The daily-use recipient is a TPM-bound key with **no PIN**, at `~/.config/sops/age/keys.txt`, where sops looks by
  default. Decryption works without a prompt, so the TPM key acts as this machine's secret zero.
- Every file is also encrypted to a **backup recipient**: a plain age key kept only in the password manager, never
  on disk except in `/dev/shm` during a restore.
- `.sops.yaml` uses the old-style `age1tpm1…` recipient (`age-plugin-tpm -y --tpm-recipient`). The default
  `age1tag1…` recipient needs `age-plugin-tag`, which Arch's `age` package doesn't ship.

## Consequences
- A copied file, a leaked backup, or a pulled disk no longer exposes secrets. But anything running as me can use
  the key, and so can a thief with the *whole* workstation: the disk is unencrypted and the key isn't bound to boot
  state (PCRs), so booting a live USB on this machine can read the sealed blob and ask the same TPM to unwrap it.
  A PIN, PCR binding, or full-disk encryption with TPM + PIN ([ideas.md](../ideas.md)) would close that.
  Accepted for now: the convenience is worth it while `secrets/` holds only homelab bootstrap credentials.
- The TPM key dies with the motherboard, a TPM clear (some BIOS updates reset firmware TPMs), or a reinstall that
  wipes it. Recovery always goes through the backup key, so the password manager is now the one place every secret
  depends on.
- Any new machine or consumer (a second workstation, Flux in step 5) needs its own recipient in `.sops.yaml`, then
  `sops updatekeys`.
- Upgrades still open: a PIN, Shamir-split paper backup, a FIDO2 key ([ideas.md](../ideas.md)).
