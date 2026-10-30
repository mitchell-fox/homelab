"""Tests for inventory.py. Run with `make test`."""

import copy
import unittest

from inventory import InventoryError, build_inventory

BASE = {
    "network": {
        "cidr": "192.168.10.0/24",
        "gateway": "192.168.10.1",
        "domain": "home.arpa",
        "dhcp": {"start": "192.168.10.100", "end": "192.168.10.199"},
        "floating_ips": {"start": "192.168.10.200", "end": "192.168.10.249"},
        "dns_servers": ["pi"],
    },
    "hosts": {
        "router": {"ip": "192.168.10.1", "mac": "TODO", "role": "gateway", "ansible": False},
        "pi": {"ip": "192.168.10.2", "mac": "aa:bb:cc:dd:ee:ff", "role": "dns"},
        "k3s-1": {"ip": "192.168.10.21", "role": "k3s-server", "vm": True},
    },
}


def with_host(name, **host):
    data = copy.deepcopy(BASE)
    data["hosts"][name] = host
    return data


class BuildInventoryTest(unittest.TestCase):
    def test_groups_by_role_with_valid_names(self):
        inv = build_inventory(BASE)
        self.assertEqual(inv["dns_hosts"]["hosts"], ["pi"])
        self.assertEqual(inv["k3s_server_hosts"]["hosts"], ["k3s-1"])

    def test_skips_hosts_with_ansible_false(self):
        inv = build_inventory(BASE)
        self.assertNotIn("gateway_hosts", inv)
        self.assertNotIn("router", inv["_meta"]["hostvars"])

    def test_hostvars(self):
        hostvars = build_inventory(BASE)["_meta"]["hostvars"]
        self.assertEqual(hostvars["pi"], {"ansible_host": "192.168.10.2", "role": "dns", "mac": "aa:bb:cc:dd:ee:ff"})
        self.assertNotIn("mac", hostvars["k3s-1"])  # no MAC known

    def test_dns_servers_resolved_to_ips(self):
        network = build_inventory(BASE)["all"]["vars"]["network"]
        self.assertEqual(network["dns_servers"], ["192.168.10.2"])
        self.assertEqual(BASE["network"]["dns_servers"], ["pi"])  # input not mutated


class ValidateTest(unittest.TestCase):
    def assertInvalid(self, data, message):
        with self.assertRaises(InventoryError) as ctx:
            build_inventory(data)
        self.assertIn(message, str(ctx.exception))

    def test_ip_outside_subnet(self):
        self.assertInvalid(with_host("old", ip="192.168.1.5", role="x"), "outside 192.168.10.0/24")

    def test_ip_in_dhcp_pool(self):
        self.assertInvalid(with_host("x", ip="192.168.10.150", role="x"), "inside the DHCP pool")

    def test_ip_in_floating_range(self):
        self.assertInvalid(with_host("x", ip="192.168.10.210", role="x"), "inside the floating IP range")

    def test_floating_range_overlaps_dhcp(self):
        data = copy.deepcopy(BASE)
        data["network"]["floating_ips"]["start"] = "192.168.10.150"
        self.assertInvalid(data, "overlaps the DHCP pool")

    def test_duplicate_ip(self):
        self.assertInvalid(with_host("x", ip="192.168.10.2", role="x"), "already used by")

    def test_missing_role(self):
        self.assertInvalid(with_host("x", ip="192.168.10.40"), "x: missing role")

    def test_unknown_dns_server(self):
        data = copy.deepcopy(BASE)
        data["network"]["dns_servers"] = ["nope"]
        self.assertInvalid(data, "'nope' is not a host key")

    def test_reports_every_error(self):
        data = with_host("a", ip="192.168.1.5", role="x")
        data["hosts"]["b"] = {"ip": "192.168.10.150", "role": "x"}
        with self.assertRaises(InventoryError) as ctx:
            build_inventory(data)
        self.assertIn("a:", str(ctx.exception))
        self.assertIn("b:", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
