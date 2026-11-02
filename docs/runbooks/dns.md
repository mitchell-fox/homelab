# Runbook: dns

The network's DNS server and ad blocker: Pi-hole in Docker Compose on the Raspberry Pi, outside the cluster.

| | |
|---|---|
| Role in `network.yaml` | `dns` |
| Hosts | `pi` |
| Hardware | Raspberry Pi 4 (8 GB), SD card |
| OS | Raspberry Pi OS (Debian 13) |
| Admin page | `http://<pi-ip>/admin` |
| Admin password | `sops decrypt --extract '["webpassword"]' secrets/pihole.sops.yaml` |
| Settings | `ansible/group_vars/dns_hosts.yml` (image version, upstreams, blocklists) |
| Related | [ADR-0007](../decisions/ADR-0007-dns-outside-cluster.md), [ADR-0018](../decisions/ADR-0018-pihole-in-docker.md), [workstation](common/workstation.md) |

## What the repo restores and what it doesn't

| Item | Restored by | If lost |
|------|-------------|---------|
| OS install, SSH key, Docker | You, by hand | Not yet automated |
| Pi-hole, its settings, blocklists | `make dns` | Nothing; rerun |
| Admin password | Nothing: `secrets/pihole.sops.yaml` is on the workstation only, not in git | Create a new file with `sops edit`, then rerun `make dns` |
| Query history | Nothing | Starts empty |
| Allowlist or denylist entries made in the web UI | Nothing | Re-enter them; not in the repo yet |

## A. Deploy or change settings

When: first install, or after editing the role or its settings. Takes about 5 minutes the first time.

Prerequisites: SSH key login works, and the key is in an agent if it has a passphrase.

1. **[script]** Apply: `make dns`
2. **[check]** Finish with the health check.

## B. Point a network at Pi-hole

When: after a working deploy.

1. **[manual]** In UniFi, set that network's DHCP DNS server to the Pi's IP.
2. **[check]** On a client, renew its lease and confirm its DNS server is the Pi.

To undo: set the DHCP DNS server back to Auto. Clients pick up the change as their leases renew.

## C. Go back to an older Pi-hole image

When: an automatic update caused a problem that its DNS check didn't catch.

1. **[manual]** Set `pihole_image` in `ansible/group_vars/dns_hosts.yml` to a specific older tag.
2. **[manual]** Stop the update timer on the Pi: `sudo systemctl disable --now pihole-update.timer`. Otherwise its
   next run updates whatever tag is set.
3. **[script]** Apply: `make dns`. This turns the timer back on, so repeat step 2 afterward.
4. **[check]** Finish with the health check.

## What updates on its own

| What | How | When |
|------|-----|------|
| Blocklists | `pihole-gravity.timer` | Daily, 03:30–04:00 |
| OS packages, including Docker | `unattended-upgrades` | Daily, around 06:00 |
| Reboot, if an update needs one | `unattended-upgrades` | 04:30 |
| Bootloader | `rpi-eeprom-update.service` | At boot |
| Pi-hole image | `pihole-update.timer`, rolls back if the new image fails its DNS check | Weekly, Tuesday 05:00–05:30 |

To see what happened: `systemctl status pihole-gravity.service`, `journalctl -u pihole-update.service`, and
`/var/log/unattended-upgrades/`.

## If the Pi is down

Every network pointed at it loses name lookups. **[manual]** Set those networks' DHCP DNS back to Auto in UniFi.
Clients on an existing lease may need to reconnect to pick that up.

## Health check

Run from a client on the LAN:

- `dig @<pi-ip> example.com +short` returns an address.
- `dig @<pi-ip> adsrvr.org +short` returns `0.0.0.0`.
- The admin page shows blocking enabled and a non-zero domain count.

## Log

| Date | Procedure | Duration | Notes |
|------|-----------|----------|-------|
| 2026-11-01 | A | About 5 min | First install |
