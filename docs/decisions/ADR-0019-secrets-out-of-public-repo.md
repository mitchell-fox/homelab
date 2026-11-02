# ADR-0019: Secrets stay out of the public repo, even encrypted

- Status: Accepted
- Date: 2026-11-01
- Amends: [ADR-0004](ADR-0004-sops-age-secrets.md), [ADR-0014](ADR-0014-secrets-two-layers.md)

## Context
ADR-0004 keeps sops-encrypted secrets in git. Today `main` pushes straight to public GitHub, so anything committed
is public and permanent. Encryption protects those files only for as long as the keys and the ciphertext hold up, and
a copy can't be recalled once published.

## Options
- **Encrypted secrets in the public repo (ADR-0004)**: one command restores everything, but ciphertext is public forever.
- **Password manager only**: nothing in any repo, but every restore is by hand, which slows a rebuild.
- **On the workstation now, then private Forgejo**: nothing public, with a one-command restore again once Forgejo runs.

## Decision
- Secret files are never committed to the public repo, even encrypted.
- Until Forgejo is `origin`, `secrets/*.sops.yaml` stays on the workstation, and `.gitignore` enforces that.
  Anything that can't be regenerated is also kept in the password manager.
- Once Forgejo is `origin`, secrets move into it, and Copybara excludes `secrets/` and any other secret material from
  the public copy (ADR-0012). The `.gitignore` entry comes out at that point. The gitleaks scan remains as a backstop.
- `.sops.yaml` stays public, since it only holds public keys.

## Consequences
- Until Forgejo runs, losing the workstation loses these files. Rebuilds rely on regenerating secrets or restoring them
  from the password manager.
- Forgejo's own bootstrap secrets can't depend on Forgejo, so those stay in the password manager.
- The Copybara filter becomes a safety control: a mistake in it could publish encrypted secrets, so it needs a test.
