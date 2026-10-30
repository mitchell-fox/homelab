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

## Status: age key moved into the TPM (done 2026-10-30)

Decision and reasoning in [ADR-0015](../decisions/ADR-0015-age-key-in-tpm.md); recovery steps in
`secrets/README.md` and the workstation runbook. What was done:

- Installed `age-plugin-tpm`, added `mfox` to `tss`.
- Generated a TPM-sealed identity with **no PIN** at `~/.config/sops/age/keys.txt`, so sops decrypts with no prompt.
- Generated a backup age key in `/dev/shm`, saved it to the password manager, shredded the file.
- `.sops.yaml` lists both recipients. Tested: the TPM key decrypts alone, and the backup key decrypts alone.
- Shredded the old plain key (it never encrypted anything).

Gotcha: `age-plugin-tpm -y` prints an `age1tag1…` recipient by default, and sops then fails with
`"tag" plugin not found: exec: "age-plugin-tag"`. `-y --tpm-recipient` prints the old `age1tpm1…` form, which
sops handles through `age-plugin-tpm` itself.
