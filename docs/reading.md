# Reading list

Articles behind the design decisions here, mostly about secrets and "secret zero" (the one secret that isn't
protected by another secret). Each entry: what it is, and why it's worth the time.

## How the big providers protect root keys

- **[Google: Default encryption at rest](https://cloud.google.com/docs/security/encryption/default-encryption)**
  The full key hierarchy, from data keys down to Root KMS and the physical safes holding its backups.
  The clearest public answer to "where does the chain end at a hyperscaler?"
- **[AWS KMS cryptographic details](https://docs.aws.amazon.com/kms/latest/cryptographic-details/intro.html)**
  How KMS HSMs keep keys from leaving in plaintext, even for AWS operators, and how quorum approval
  works for HSM changes. Long; read the intro and the sections on domains and quorum.
- **[Google: Titan hardware chip](https://cloud.google.com/docs/security/titan-hardware-chip)**
  Hardware root of trust and measured boot: how a machine proves its identity without a stored password.
- **[Google: ALTS](https://cloud.google.com/docs/security/encryption-in-transit/application-layer-transport-security)**
  Service-to-service identity built on those machine identities. Google's internal version of SPIFFE.
- **[SPIFFE overview](https://spiffe.io/docs/latest/spiffe-about/overview/)**
  The open standard for workload identity. The self-hosted way to get what Azure managed identity gives you.
- **[IANA: DNSSEC root key signing ceremonies](https://www.iana.org/dnssec/ceremonies)**
  A public M-of-N key ceremony, with recordings. Quorum done in the open.
- **[Azure Managed HSM security domain](https://learn.microsoft.com/en-us/azure/key-vault/managed-hsm/security-domain)**
  Azure's closest match to OpenBao's Shamir unseal: restoring the HSM needs a quorum of your own keys.

## Incidents: what happens when a root of trust leaks

- **[CSRB review of the 2023 Microsoft Exchange Online intrusion](https://cisa.gov/resources-tools/resources/CSRB-Review-Summer-2023-MEO-Intrusion)**
  Storm-0558: a stolen consumer signing key, plus missing issuer checks, gave access to government email.
  The best case study of "an identity signing key is secret zero for everything that trusts it."
  [Schneier's summary](https://www.schneier.com/blog/archives/2024/04/us-cyber-safety-review-board-on-the-2023-microsoft-exchange-hack.html)
  first if short on time.
- **[Microsoft: Storm-0558 key acquisition investigation](https://www.microsoft.com/en-us/msrc/blog/2023/09/results-of-major-technical-investigations-for-storm-0558-key-acquisition)**
  Microsoft's own account. Read the March 2024 update at the bottom: the crash dump theory was walked back.
- **[CyberArk: Golden SAML](https://www.cyberark.com/resources/threat-research-blog/golden-saml-newly-discovered-attack-technique-forges-authentication-to-cloud-apps)**
  The original write-up of forging sign-ins with a stolen AD FS token-signing certificate (later used in SolarWinds).
- **[Uber: September 2022 security update](https://www.uber.com/newsroom/security-update/)**
  Uber's official account: a bought contractor password and MFA fatigue. The hardcoded admin password for
  their privileged-access vault comes from the attacker's own claims and outside researchers, not this post.
- **DigiNotar (2011), Fox-IT's "Black Tulip" report.** A certificate authority breached and bankrupt within weeks.
  Search for the report by name; no stable link checked yet.

## OpenBao

- **[Threat model](https://openbao.org/docs/next/internals/security/)**
  What OpenBao defends against and what it explicitly doesn't. Read before reporting anything security-related.
- **[Seal/unseal](https://openbao.org/docs/concepts/seal/)**
  Shamir shares, auto-unseal, and the barrier. Step 1 of the learning plan.
- **[Shamir, "How to Share a Secret" (1979)](https://web.mit.edu/6.857/OldStuff/Fall03/ref/Shamir-HowToShareASecret.pdf)**
  The original paper. Two pages of math, very readable.

## Tools used in this repo

- **[sops docs](https://getsops.io/docs/)** and the **[age spec](https://age-encryption.org/v1)** (ADR-0004).
- **[Flux: Manage secrets with sops](https://fluxcd.io/flux/guides/mozilla-sops/)** For rollout step 5.
- **[age-plugin-yubikey](https://github.com/str4d/age-plugin-yubikey)** An age key generated on a YubiKey that can't
  be copied off it. Requires PIV, which the YubiKey 5 series has and the Security Key series doesn't
  ([Yubico PIV docs](https://developers.yubico.com/PIV/)).
- **[age-plugin-tpm](https://github.com/Foxboron/age-plugin-tpm)** The same idea using the workstation's built-in TPM. Free.
- **[age-plugin-fido2-hmac](https://github.com/olastor/age-plugin-fido2-hmac)** Uses any FIDO2 key with the
  `hmac-secret` extension, including cheaper keys without PIV.
- **[age-plugin-sss](https://github.com/olastor/age-plugin-sss)** Shamir secret sharing for age recipients
  ("any 2 of these 3 keys"). The same idea as OpenBao's unseal shares.
- **sops age plugin support:** added in 3.10 ([getsops/sops#1641](https://github.com/getsops/sops/pull/1641)).

## Azure comparison

- **[App Configuration: Key Vault references in .NET](https://learn.microsoft.com/en-us/azure/azure-app-configuration/use-key-vault-references-dotnet-core)**
  Shows that the client resolves references with the app's own identity, not App Configuration's.
