# Runbook: renumber the network

> **Status:** draft. The `make` targets referenced below are not built yet.

This is the procedure the whole repo exists for: a subnet change should be a one-line diff to
`inventory/network.yaml` plus the steps below.

## A. Subnet, IP, or NIC change

**When:** the ISP changes the subnet, a host gets a new IP, or a NIC (and so its MAC) is replaced.
**Prereqs:** a working workstation ([workstation](workstation.md)).

1. **[manual]** Edit `inventory/network.yaml`:
   - **Subnet change:** `network.cidr`, `gateway`, the DHCP range, and the host IPs.
   - **New NIC:** that host's `mac:`.
2. **[script]** Apply the network side (subnet, DHCP reservations, firewall):
   ```
   make unifi
   ```
3. **[script]** Update the DNS records on the Pi:
   ```
   make dns
   ```
4. **[manual]** Renew addresses: reboot the affected hosts, or wait out the DHCP lease.
5. **[script]** Reapply every host whose config is built from the network settings (firewall rules use `network.cidr`):
   ```
   make all
   ```
6. **[check]** Run the health check in each affected role's runbook, from a machine on the LAN.
7. **[manual]** Commit, and add a row to the log.

## Logs

| Date | Change | Time taken | Notes |
|------|--------|------------|-------|
| | | | |
