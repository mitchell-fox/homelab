# Learning notes: secrets, secret zero, and OpenBao

What I learned on 2026-10-30, and where the TPM work stands. Sources are in [reading.md](../reading.md).
These are notes, not decisions; decisions go in [ADRs](../decisions/).

## Secret zero

- Every encrypted secret needs a key, and that key needs protecting too. Whatever sits at the bottom, a secret
  not protected by another secret, is **secret zero**. It can be moved, never removed.
- Every chain ends in one of three places: **a person's memory** (a master password, unseal key holders),
  **hardware the key can't be copied out of** (TPM, HSM, YubiKey), or **a platform vouching for you**
  (Azure managed identity, Kubernetes service account tokens).
- **In this repo:** `secrets/*.sops.yaml` → age private key on the workstation → backup in the password manager
  → master password in my head. The public key in `.sops.yaml` only encrypts, so it's safe in git.
- Two ways it fails: **lose it** (every secret unreadable) or **leak it** (every secret exposed, including old
  versions in git history; removing a recipient later doesn't fix those, you must rotate the real values).
- Rules for a good secret zero: as few as possible, hard to copy, one per machine so they can be revoked one at a
  time, and a recovery path that's actually been tested.

## How hyperscalers do it

- **Root keys in HSMs** that can't export them; software can use a key but never read it.
- **Layers of keys (envelope encryption):** data keys wrapped by KMS keys, wrapped by a root key. Google's chain
  ends with Root KMS backups in physical safes, so it still ends with hardware and people.
- **Hardware machine identity** (Titan, Cerberus/Pluton, Nitro) instead of passwords in config files.
  SPIFFE is the open standard for the same idea.
- **Quorum (M-of-N)** for sensitive operations, like the public DNSSEC root key ceremony.
- **Key point: HSMs stop theft, not misuse.** An attacker with access can use a key while they're in, but can't
  take it with them, so cutting access ends the compromise.
- **Real breaches steal something one level up from the root:** a signing key outside the HSM (Storm-0558),
  AD FS token-signing certificates (Golden SAML), a bought contractor password (Uber), a whole CA (DigiNotar).

## OpenBao vs. Azure Key Vault

- OpenBao is a **secret broker** (creates credentials on demand, revokes them via leases); Key Vault is mostly a
  **secret store**. Biggest gap: dynamic secrets, which Azure answers with "no secret at all" (managed identity).
- Close matches: KV v2 ≈ Secrets, Transit ≈ Keys. Partial: PKI ≈ Certificates (OpenBao is the CA itself).
  Seal/unseal has no Key Vault equivalent; Managed HSM's security domain (quorum restore) is the closest.
- App Configuration never reads Key Vault: the client resolves references with the **app's own** identity.
  OpenBao has no App Config; Agent templates, External Secrets Operator, or the API fill that role. In this lab,
  git is the config store ([ADR-0014](../decisions/ADR-0014-secrets-two-layers.md)).
- **Open question for ADR-0014:** it assumes auto-unseal needs a cloud KMS. OpenBao also has transit and PKCS#11
  seals; check whether any of them can use a TPM before settling on manual unseal.

## Contributing to OpenBao

- OpenBao is a Go fork of HashiCorp Vault (after Vault's 2023 license change), so Go is inherited, not chosen.
- **No AI-generated code, issues, PR text, or security reports** (CONTRIBUTING.md, AGENTS.md); DCO sign-off is
  required. AI is fine for learning, search, and debugging. Write everything myself; turn off editor AI there.
- Plan: concepts (seal, barrier, auth methods, secrets engines, leases, policies) → run `bao server -dev` →
  trace a request through the code → join GitHub Discussions / the dev working group → pick a good first issue
  (#1768, #2845, #1864, #1677, #1867 were open and unassigned on 2026-10-30).
- It's a side project; DataFusion stays the main open-source target (Rust).

## Status: moving the age key into the TPM

Plan in [ideas.md](../ideas.md) ("Move the age key into the workstation's TPM"). `secrets/` holds no encrypted
files yet, so nothing needs re-encrypting and the old key never protected anything.

- [ ] **0. Install** (separate terminal), then log out and back in:
  ```fish
  paru -S age-plugin-tpm
  sudo usermod -aG tss mfox
  ```
- [ ] **1. Check:** `groups` lists `tss`, and `age-plugin-tpm --help` runs.
- [ ] **2. Put the old key aside** (deleted in step 7, once the new setup works):
  ```fish
  mv ~/.config/sops/age/keys.txt ~/.config/sops/age/keys.txt.old
  ```
- [ ] **3. Create the TPM key** where sops looks by default. Decide on `--pin` first (stops someone at an
  unlocked session from decrypting; costs a prompt on every decrypt):
  ```fish
  age-plugin-tpm --generate --pin -o ~/.config/sops/age/keys.txt
  chmod 600 ~/.config/sops/age/keys.txt
  age-plugin-tpm -y ~/.config/sops/age/keys.txt   # prints the recipient for .sops.yaml
  ```
  The file is a sealed blob, useless without this machine's TPM.
- [ ] **4. Create the paper backup key in RAM only** (`/dev/shm`), copy it to paper, then destroy the file:
  ```fish
  age-keygen -o /dev/shm/backup.txt   # prints the public key; note it
  cat /dev/shm/backup.txt             # write down or print the AGE-SECRET-KEY-1... line
  shred -u /dev/shm/backup.txt
  ```
  Printing passes through the print spooler on disk; hand-copying avoids that but is error-prone.
  Step 6 catches copying mistakes. Decide where the paper lives (and whether a password-manager copy is allowed).
- [ ] **5. Update `.sops.yaml`:** replace the old recipient with both new ones (comma-separated `age:` value),
  with a comment saying which is the TPM key and which is the paper backup.
- [ ] **6. Test both keys separately:**
  ```fish
  sops edit secrets/test.sops.yaml          # add: hello: world
  sops decrypt secrets/test.sops.yaml       # works via the TPM key
  mv ~/.config/sops/age/keys.txt ~/.config/sops/age/keys.txt.tpm
  # type the paper key into /dev/shm/restore.txt
  SOPS_AGE_KEY_FILE=/dev/shm/restore.txt sops decrypt secrets/test.sops.yaml   # works via paper only
  shred -u /dev/shm/restore.txt
  mv ~/.config/sops/age/keys.txt.tpm ~/.config/sops/age/keys.txt
  rm secrets/test.sops.yaml
  ```
- [ ] **7. Retire the old key:** `shred -u ~/.config/sops/age/keys.txt.old`, and remove it from the password manager.
- [ ] **8. Docs:** update `secrets/README.md` and the workstation runbook (key location, recovery from paper),
  and write ADR-0015 (age key in the TPM, amends ADR-0004).
