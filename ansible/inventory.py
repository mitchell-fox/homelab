#!/usr/bin/env python3
"""Ansible dynamic inventory generated from inventory/network.yaml (ADR-0003, ADR-0011).

Each host joins the group `<role>_hosts` (dashes become underscores, since Ansible group names must be valid
identifiers), so `ansible/group_vars/<role>_hosts.yml` applies to it. The suffix keeps groups from clashing with
host keys like `llm` and `git`, which double as DNS names (`llm.home.arpa`). Hosts with
`ansible: false` (the router, which Terraform manages) are left out.

The network section is exposed to every host as the `network` variable, with `dns_servers` resolved from
host keys to IPs, so roles never need an IP of their own.

The file is validated on every run, so a bad edit fails here instead of halfway through a playbook.

Usage (Ansible calls it this way):
    ansible/inventory.py --list
    ansible/inventory.py --host <name>
"""

import argparse
import ipaddress
import json
import re
import sys
from pathlib import Path

import yaml

NETWORK_YAML = Path(__file__).resolve().parent.parent / "inventory" / "network.yaml"


class InventoryError(Exception):
    pass


def group_name(role: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", role) + "_hosts"


def validate(data: dict) -> None:
    """Raise InventoryError listing every problem found, not just the first."""
    errors = []
    net = data["network"]
    subnet = ipaddress.ip_network(net["cidr"])
    dhcp_start = ipaddress.ip_address(net["dhcp"]["start"])
    dhcp_end = ipaddress.ip_address(net["dhcp"]["end"])
    hosts = data.get("hosts") or {}

    if ipaddress.ip_address(net["gateway"]) not in subnet:
        errors.append(f"gateway {net['gateway']} is outside {subnet}")
    if not (dhcp_start in subnet and dhcp_end in subnet and dhcp_start <= dhcp_end):
        errors.append(f"DHCP range {dhcp_start}-{dhcp_end} is not a valid range inside {subnet}")

    seen = {}
    for name, host in hosts.items():
        if "role" not in host:
            errors.append(f"{name}: missing role")
        try:
            ip = ipaddress.ip_address(host["ip"])
        except (KeyError, ValueError):
            errors.append(f"{name}: missing or invalid ip {host.get('ip')!r}")
            continue
        if ip not in subnet:
            errors.append(f"{name}: {ip} is outside {subnet}")
        if dhcp_start <= ip <= dhcp_end:
            errors.append(f"{name}: {ip} is inside the DHCP pool {dhcp_start}-{dhcp_end}")
        if ip in seen:
            errors.append(f"{name}: {ip} is already used by {seen[ip]}")
        seen[ip] = name

    for server in net.get("dns_servers", []):
        if server not in hosts:
            errors.append(f"dns_servers: {server!r} is not a host key")

    if errors:
        raise InventoryError("inventory/network.yaml is invalid:\n  " + "\n  ".join(errors))


def build_inventory(data: dict) -> dict:
    validate(data)
    hosts = data.get("hosts") or {}

    network = dict(data["network"])
    network["dns_servers"] = [hosts[s]["ip"] for s in network.get("dns_servers", [])]

    inventory = {"all": {"vars": {"network": network}}, "_meta": {"hostvars": {}}}
    for name, host in sorted(hosts.items()):
        if host.get("ansible", True) is False:
            continue
        group = inventory.setdefault(group_name(host["role"]), {"hosts": []})
        group["hosts"].append(name)

        hostvars = {"ansible_host": host["ip"], "role": host["role"]}
        if host.get("mac") not in (None, "TODO"):
            hostvars["mac"] = host["mac"]
        inventory["_meta"]["hostvars"][name] = hostvars
    return inventory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true")
    mode.add_argument("--host")
    args = parser.parse_args()

    try:
        inventory = build_inventory(yaml.safe_load(NETWORK_YAML.read_text()))
    except InventoryError as e:
        print(e, file=sys.stderr)
        return 1

    if args.host:
        # Hostvars are already in _meta, so Ansible never calls this; kept for the protocol.
        print(json.dumps(inventory["_meta"]["hostvars"].get(args.host, {}), indent=2))
    else:
        print(json.dumps(inventory, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
