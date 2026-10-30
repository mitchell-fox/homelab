# ADR-0009: LAN LLM host on bare metal, llama.cpp on Vulkan, Open WebUI in front

- Status: Accepted
- Date: 2026-10-30

## Context
I want one machine that serves an LLM to everything on the LAN: a web UI for people, and an
OpenAI-compatible API for tools (editor plugins, scripts, Home Assistant). It has to be free and run offline.

The hardware is a laptop: Ryzen 7 2700, 64 GB RAM, and a Radeon RX Vega 56 with 8 GB of HBM2, running
Ubuntu Server 26.04 LTS. The target model is Qwen 3.6 35B-A3B, a mixture-of-experts model: 35B parameters
in total, about 3B active per token. That's roughly 20–22 GB at Q4_K_M, so it can't fit in VRAM.

AMD's ROCm has dropped support for Vega 10 (gfx900).

## Options
- **Inference engine**
  - **Ollama**: easiest, but it hides the setting that decides which parts of the model go on the CPU
    and which on the GPU. ROCm doesn't support this GPU, and its Vulkan support is newer.
  - **vLLM**: built for big GPUs and ROCm/CUDA. Wrong fit.
  - **llama.cpp (`llama-server`) on Vulkan**: works on Vega through Mesa's RADV driver, which ships with Ubuntu.
    `--n-cpu-moe` keeps attention layers and the KV cache on the GPU and puts the expert weights in system RAM.
    It serves an OpenAI-compatible API.
- **GPU backend**
  - **ROCm**: unsupported on gfx900, and pinning old versions is fragile.
  - **Vulkan**: supported, no vendor driver needed.
- **Where it runs**
  - **In k3s**: needs GPU passthrough plus device plugins. Lots of complexity for one box.
  - **Bare metal, managed by Ansible**: same reasoning as DNS (ADR-0007).
- **Web UI**
  - **Open WebUI**: user accounts, chat history, per-user API keys.
  - **llama-server's built-in UI**: no accounts.

## Decision
- **Engine:** `llama-server` from llama.cpp's prebuilt Vulkan release, pinned to a specific version.
- **Process:** runs as a systemd service.
- **Web UI:** Open WebUI in Docker, pointed at it.
- **Location:** bare metal, outside the cluster, configured by an Ansible role named `llm`.
- **Settings in `ansible/group_vars/llm.yml`.** Starting values:
  - Model: Qwen 3.6 35B-A3B, Q4_K_M.
  - `ctx_size: 65536`, with 2 parallel slots.
  - KV cache quantized to q8_0, with flash attention on.
  - `n_cpu_moe` tuned until VRAM is nearly full.
- **Access:** LAN only. ufw allows ports 3000 (UI) and 8080 (API) from `network.cidr` alone. The API needs a
  bearer key, stored in sops.
- **Laptop-as-server settings, also managed by Ansible:**
  - logind ignores the lid switch, suspend key, and idle.
  - The sleep, suspend, hibernate, and hybrid-sleep targets are masked.
  - Battery charging is capped at about 80% where the firmware allows it.
  - Wired ethernet only.

## Consequences
- Expect roughly 10–20 tokens/sec when generating; this is an estimate, so measure it.
  Long prompts are slow to read in. That's fine for chat, but slow for big-document work.
- One GPU, shared. Requests beyond the number of slots wait in a queue, and each slot gets `ctx_size / slots`.
- More context means less room on the GPU, so more experts move to the CPU and generation gets slower.
  Results go in the tuning log in `docs/runbooks/llm.md`.
- A laptop has its own risks:
  - The battery can swell after years of constant charge; inspect it now and then.
  - It can run hot with the lid closed; check temperatures under load.
  - It may not power back on by itself after a long outage. Set this in the BIOS by hand if the option exists.
- Open WebUI's accounts and chat history live in a Docker volume. Whether to back them up is still open.
  Until that's decided, a rebuild loses them.
