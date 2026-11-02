# ADR-0018: Pi-hole in Docker Compose on the Pi

- Status: Accepted
- Date: 2026-11-01

## Context
ADR-0007 put DNS on the Pi and left the choice of AdGuard Home or Pi-hole for later. The Pi already runs
Raspberry Pi OS with Docker Compose services under `/data/services/`. Rebuilding it must be one command (ADR-0011),
with the admin password out of plaintext (ADR-0004).

## Options
- **Pi-hole, native install**: DNS doesn't depend on Docker, but it's harder to pin and reproduce.
- **Pi-hole in Docker Compose**: one pinned image and one compose file, matching what's already on the Pi.
- **AdGuard Home**: a capable alternative, with no strong reason to prefer it here.

Within Docker, **bridge** networking gives more isolation, but **host** networking avoids NAT, so client IPs can't
be hidden by it, and there are no port mappings to maintain.

## Decision
- Pi-hole in Docker Compose with host networking, managed by `make dns`.
- The image tracks `latest` and updates weekly by timer, keeping up with security releases without anyone having to
  remember. If the new image doesn't answer DNS, the script returns to the previous one. This is a deliberate
  exception to ADR-0011's pinning.
- Upstreams are Quad9. Pi-hole's own DNSSEC stays off, because Quad9 validates and a Pi with no battery-backed
  clock can fail validation after a power cut.
- The Pi resolves names through Quad9 directly, ignoring DHCP, so it never depends on its own Pi-hole.
- One blocklist, HaGeZi Multi PRO, chosen over Normal because someone is on hand to allowlist false positives.
  Measured on 2026-11-01, it fully covers HaGeZi Normal and 99.6% of OISD small, so stacking those adds nothing.
  Blocklists are reconciled through Pi-hole's API, since no config option sets them.
- HaGeZi's full Threat Intelligence Feeds as well, so malware blocking doesn't depend only on Quad9 and is
  already in place if the upstream changes. The Pi 4 has the memory for its roughly 1.85 million domains.
- OS packages update daily through `unattended-upgrades`, from Debian, Raspberry Pi and Docker, rebooting at
  04:30 only when an update requires it. A systemd timer refreshes blocklists daily, instead of the image's weekly job.
- To reduce SD card wear, query history is written every 5 minutes, kept for 30 days, and `pihole.log` is off.

## Consequences
- DNS depends on Docker being healthy on the Pi, as well as the Pi itself. It's still a single point of failure.
- The admin password's sops file isn't committed (ADR-0019). If the workstation is lost, generate a new password and
  rerun `make dns`.
- A power cut can lose up to 5 minutes of query history.
- The daily list refresh rewrites a database of about 120 MB on the SD card, which adds wear. An SSD would avoid that.
- Unattended updates can break DNS with nobody watching, and a reboot or Docker update briefly interrupts it.
- A rebuild may get a newer Pi-hole than the last one, unlike everything else in the repo.
- Rollback only covers a new image that fails its check. A database migration could stop the old image from
  working, and a problem that only appears later needs a person. Nothing alerts on failures yet (see `docs/ideas.md`).
- HaGeZi Pro doesn't list some well-known Google ad domains, such as `doubleclick.net`, so don't assume
  a domain is blocked. Local rules can add them if that matters.
- The list of blocklists is owned by the repo: `make dns` removes any added by hand in the web UI.
