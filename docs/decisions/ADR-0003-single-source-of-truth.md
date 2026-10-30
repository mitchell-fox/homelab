# ADR-0003: `inventory/network.yaml` as the single source of truth

- Status: Accepted
- Date: 2026-10-30

## Context
The ISP equipment swap forced a renumbering from 192.168.1.0/24 to 192.168.10.0/24. IPs were scattered
across the router UI, DNS records, VM configs, and notes. The goal is that the next renumbering is a one-line diff.

## Options
- **Terraform variables**: fine for Terraform, but Ansible would need its own copy.
- **Ansible inventory as the master**: Terraform can't read it cleanly.
- **NetBox or another IPAM tool**: the right answer at company scale, too heavy for one /24.
- **A plain YAML file**: both tools read it natively (Terraform `yamldecode`, Ansible `vars_files`),
  and it's easy to review in a diff.

## Decision
`inventory/network.yaml` holds the subnet, gateway, DHCP range, and every host's IP and MAC.
Nothing else in the repo hardcodes an IP.

## Consequences
- The schema is informal. If it grows, add a JSON Schema and validate it in CI.
- Host IPs are listed explicitly rather than computed with `cidrhost()` offsets. That's easier to read,
  but a subnet change means editing every host line. Revisit if that becomes painful.
