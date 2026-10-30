# Runbook: llm

> **Status:** draft. The Ansible role, inventory script, `make` targets, and `secrets/llm.sops.yaml`
> referenced below are not built yet. Steps marked [script] describe how they will work.

The LAN's shared LLM server. It runs llama.cpp (`llama-server`) on the Vega 56 via Vulkan,
with Open WebUI in front. It is bare metal, managed by Ansible, and outside the k3s cluster.

| | |
|---|---|
| Role in `network.yaml` | `llm` |
| Hosts | `llm` (`llm.home.arpa`) |
| Hardware | Laptop: Ryzen 7 2700, 64 GB RAM, Radeon RX Vega 56 (8 GB HBM2). Runs lid-closed, never sleeps. |
| OS | Ubuntu Server LTS |
| Web UI | `http://llm.home.arpa:3000` |
| API (OpenAI-compatible) | `http://llm.home.arpa:8080/v1`, bearer key from `secrets/llm.sops.yaml` |
| Services | `llama-server.service` (systemd), `open-webui` (Docker compose) |
| Settings | `ansible/group_vars/llm.yml` (model, context size, slots, `n_cpu_moe`) |
| Related | [ADR-0009](../decisions/ADR-0009-llm-host.md), [workstation](common/workstation.md), [renumber](common/renumber.md) |

## What the repo restores and what it doesn't

| Item | Restored by | If lost |
|------|-------------|---------|
| OS install | You (procedure A, step 1) | ~15 min by hand |
| BIOS/UEFI settings (power-on after AC loss, if offered) | You, by hand | Box stays off after a long power cut |
| Lid, sleep, and battery charge-limit settings | `make llm` | Nothing; rerun |
| Packages, llama.cpp, services, firewall | `make llm` | Nothing; rerun |
| Model file (~20 GB) | `make llm` (downloads it, checks the checksum) | Download time only |
| API key | `secrets/llm.sops.yaml` | Nothing, if you have the age key ([workstation](common/workstation.md)) |
| Open WebUI accounts and chat history | Volume backup (procedure E), if enabled | Users re-register; history gone |

---

## A. Rebuild from scratch

**When:** the disk died, the OS is broken, or you're running the DR test.
**Prereqs:** a working workstation ([workstation](common/workstation.md)), an Ubuntu Server USB stick.
**Expected time:** ~15 min hands-on, plus model download.

1. **[manual]** Install Ubuntu Server LTS.
   - Use the whole disk; the defaults are fine.
   - Username: `TODO` (must match `ansible_user` in the inventory).
   - Tick **Install OpenSSH server**, then **Import SSH identity from GitHub** using your username.
   - Skip the "featured snaps" screen.
2. **[manual]** Reboot, unplug the USB stick, and log in once at the console to confirm it booted.
3. **[check]** It got its reserved IP. The UniFi DHCP reservation is keyed to the MAC address,
   so the same hardware gets the same IP.
   ```
   ping llm.home.arpa
   ```
   If the NIC changed, run [renumber](common/renumber.md) first.
4. **[check]** SSH works without a password:
   ```
   ssh <user>@llm.home.arpa true
   ```
   If the host key changed after a reinstall, first run `ssh-keygen -R llm.home.arpa`.
5. **[script]** Provision everything:
   ```
   make llm
   ```
   This installs the Vulkan drivers, llama.cpp (pinned version), Docker, and Open WebUI. It also downloads
   the model, writes the systemd unit, sets up ufw, and starts the services. Safe to rerun if it fails partway.
6. **[check]** Health check (procedure F).
7. **[manual]** If you restore chat history, run procedure E's restore steps.
   Otherwise open the web UI and create the admin account. The first account created becomes admin,
   so do this before anyone else on the LAN does.
8. **[manual]** Add a row to the run log, with the time taken.

## B. Routine update

**When:** monthly, or when you want a newer llama.cpp or Open WebUI.
**Expected time:** ~10 min.

1. **[manual]** Bump the pinned versions in `ansible/group_vars/llm.yml` (`llama_cpp_version`,
   `open_webui_image`). Check the release notes for breaking flag changes.
2. **[script]** Update OS packages:
   ```
   make llm-os-update
   ```
   This runs apt upgrade and reboots only if the kernel changed.
3. **[script]** Apply the new versions:
   ```
   make llm
   ```
4. **[check]** Health check (procedure F).
5. **[manual]** Commit the version bump.

## C. Change the model, context size, or slots

**When:** you're trying a different model or tuning speed against context size.

1. **[manual]** Edit `ansible/group_vars/llm.yml`:
   - **Model:** `model_url`, `model_sha256`, `model_file`.
   - **Context:** `ctx_size` is the *total* context; each slot gets `ctx_size / parallel_slots`.
   - **VRAM fit:** `n_cpu_moe` is the number of layers whose experts run on the CPU. Lower is faster
     but uses more VRAM.
2. **[script]** Apply. It restarts `llama-server` only if the config changed:
   ```
   make llm
   ```
3. **[check]** Health check (procedure F), and watch VRAM use while sending a long prompt:
   ```
   ssh llm.home.arpa radeontop
   ```
   - Out-of-memory errors in `journalctl -u llama-server`: raise `n_cpu_moe` or lower `ctx_size`.
   - VRAM use well under 7 GB: lower `n_cpu_moe` by 2 and repeat.
4. **[manual]** Record the result (settings, tokens/sec, VRAM used) in the tuning log. Then commit.

Starting point: `ctx_size: 65536`, `parallel_slots: 2`, q8_0 KV cache, `n_cpu_moe: 28`.

## D. Rotate the API key

**When:** the key leaked, or someone shouldn't have access any more.

1. **[manual]** Edit the secret (sops decrypts and re-encrypts it in your editor):
   ```
   sops secrets/llm.sops.yaml
   ```
   Generate a new key with `openssl rand -hex 32`.
2. **[script]** Apply:
   ```
   make llm
   ```
3. **[manual]** Update every client that uses the raw API (editor plugins, scripts, Home Assistant).
   Open WebUI users are unaffected.
4. **[manual]** Commit the encrypted file.

## E. Back up and restore Open WebUI data (optional)

**When:** backups run weekly if `open_webui_backup: true`. Restore after procedure A.
**Decision:** TODO. Either enable this, or accept losing chat history on a rebuild and record that in a new ADR
that amends [ADR-0009](../decisions/ADR-0009-llm-host.md).

- **[script]** Back up now:
  ```
  make llm-backup
  ```
  This copies the Open WebUI volume to the backup location.
- **[script]** Restore:
  ```
  make llm-restore
  ```
  This stops Open WebUI, restores the volume, and starts it again.

## F. Health check

Run after every procedure above. All checks should pass.

```
# GPU visible to Vulkan (expect "RADV VEGA10")
ssh llm.home.arpa vulkaninfo --summary | grep deviceName

# Service running
ssh llm.home.arpa systemctl is-active llama-server

# API answers (key from: sops -d secrets/llm.sops.yaml)
curl -s -H "Authorization: Bearer $KEY" http://llm.home.arpa:8080/v1/models

# Generation works and is fast enough (check "predicted_per_second" in the timings)
curl -s -H "Authorization: Bearer $KEY" http://llm.home.arpa:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Say hi in five words."}]}'

# Web UI loads
curl -sI http://llm.home.arpa:3000 | head -1
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `vulkaninfo` shows only `llvmpipe` | Mesa Vulkan driver missing, or GPU not detected | `make llm` again; then `lspci \| grep VGA` |
| `llama-server` restarting in a loop | Out of VRAM | `journalctl -u llama-server -n 50`; raise `n_cpu_moe` or lower `ctx_size` |
| Very slow first response on long prompts | Normal: reading prompts on this hardware is slow | Shorter prompts, or fewer, larger slots |
| Requests hang while others run | Every slot is busy; requests queue | Expected with more users than `parallel_slots` |
| Can't connect from the LAN | ufw rules, or the box got a different IP | `ssh llm.home.arpa sudo ufw status`; [renumber](common/renumber.md) |
| `sops -d` fails | age key missing on the workstation | [workstation](common/workstation.md) |

## Logs

### Run log

| Date | Procedure | Time taken | Notes |
|------|-----------|------------|-------|
| | | | |

### Tuning log

| Date | Model / quant | ctx_size | slots | n_cpu_moe | VRAM used | Gen tok/s | Notes |
|------|---------------|----------|-------|-----------|-----------|-----------|-------|
| | | | | | | | |
