# Ideas backlog

Things to implement or consider later. Nothing here is decided. When an idea gets picked up, it becomes
an ADR (for a decision) or a roadmap step (for work), and the entry moves to **Done / promoted** with a link.

Each entry: what it is, why it's worth doing, and when it makes sense (the trigger or the rollout step it depends on).

## Infrastructure

- **Local git server (Forgejo), with GitHub as a public mirror.**
  Why: Flux pulling from GitHub means the cluster needs the internet to deploy, which breaks the offline constraint.
  When: before or during step 5 (k3s + Flux). Decide where it runs; outside the cluster avoids a chicken-and-egg problem.
- **Move Terraform state to the `pg` backend on self-hosted Postgres.**
  Why: survives losing the laptop, adds locking, and is Postgres practice (see ADR-0008).
  When: once Postgres runs somewhere Terraform doesn't manage, such as the Pi.
- **Add the LLM host to `inventory/network.yaml`.**
  Why: `docs/runbooks/llm-host.md` refers to host key `llm`, which doesn't exist yet.
  When: at the latest, when the LLM host's Ansible role is built.

## Azure-equivalent tools (for upskilling)

- **Prometheus + Grafana** (Azure Monitor managed Prometheus/Grafana): cluster and host monitoring. After step 5.
- **Keycloak or Authentik** (Entra ID): single sign-on via OIDC for lab services. After a few services exist.
- **Harbor** (Azure Container Registry): a local image registry, which also helps the cluster stay offline.
- **Azurite** (Azure Storage emulator): local blob, queue and table storage for apps I write.

## Quality and tooling

- **JSON Schema for `network.yaml`, validated in CI or a pre-commit hook.**
  Why: the schema is informal (ADR-0003); a typo in an IP or MAC should fail fast.
- **Compute host IPs with `cidrhost()` offsets instead of literal IPs.**
  Why: makes a renumbering a true one-line change (ADR-0003 consequences). Weigh against readability.
- **Pre-commit hook that rejects unencrypted files in `secrets/`.**
  Why: one `git add` of a plaintext file in a public repo leaks it for good. Check for the `sops:` metadata key.
  When: soon; cheap insurance before real secrets land.
- **Second age recipient as an offline backup key.**
  Why: a backup key kept offline (printed or on a USB stick) keeps secrets decryptable if the laptop and
  the password manager are both lost. Flux will need its own key in step 5 anyway.
  When: before the DR test (step 6), at the latest.
- **Hand out the router as secondary DNS via DHCP.**
  Why: the Pi is a single point of failure for DNS (ADR-0007). Do it in step 3.

## Done / promoted

_Nothing yet._
