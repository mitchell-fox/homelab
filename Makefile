# Entry point for everything Ansible (ADR-0011). Runbooks only ever say `make <target>`.
export ANSIBLE_CONFIG := $(CURDIR)/ansible/ansible.cfg

.DEFAULT_GOAL := help
.PHONY: help test inventory ping dns

help: ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  make %-12s %s\n", $$1, $$2}'

test: ## Run the inventory script's tests
	cd ansible && python3 -m unittest -v test_inventory

inventory: ## Show hosts grouped by role (validates network.yaml)
	ansible-inventory --graph --vars

ping: ## Check Ansible can reach every host
	ansible all -m ansible.builtin.ping

dns: ## Configure the DNS host (Pi-hole)
	ansible-playbook ansible/dns.yml
