# AGENTS.md — quadlet

Podman quadlet definitions for the always-on Fedora server and the kitchen Raspberry Pi.

## Layout
- `quadlet/` — server (`melody@192.168.0.2`, Fedora). Pods: `smarthome.pod` (HA, LVA, Ollama,
  Qwen3-ASR, Kokoro, Music Assistant, mosquitto, matter-server, rest980, sendspin), `net.pod`
  (nginx-proxy-manager for `*.melhome.me`), plus immich/bots/etc.
- `rpi_quadlet/` — kitchen Pi (LVA `lva_kitchen` + Jabra helper, BT proxy, sendspin, WoL).
- Home Assistant itself is documented in `~/Projects/home-assistant-server/AGENTS.md`.

## Deploying
- Push to GitHub → webhook → [quadlet-sync](https://github.com/machineonamission/quadlet-sync)
  rsyncs the repo into `/etc/containers/systemd` (anything not in the repo is DELETED there).
- **Sync does not restart containers.** After a push, restart the changed units by hand
  (`systemctl restart <unit>` on the host, or Cockpit).

## Gotchas
- quadlet-sync **flattens** the repo: every file under `quadlet/` (or `rpi_quadlet/`) lands
  directly in `/etc/containers/systemd/`, so non-unit files need globally unique names.
- **LVA sitecustomize shim** (`*/smarthome/lva/lva_sitecustomize.py`, mounted as
  `/app/patches/sitecustomize.py` with `PYTHONPATH=/app/patches`, identical in both dirs).
  HA 2026.12 (core #190096) multiplies satellite audio by `audio_settings.volume_multiplier`.
  LVA never sends audio_settings, so HA reads protobuf 0.0 and the audio becomes silence; Qwen3-ASR
  then transcribes it as "Ahora.". The shim makes LVA send 1.0. Drop it once HA or LVA fixes this.
  (Pinning older LVA nightlies does NOT help: it's the HA side.)
- Qwen3-ASR (`smarthome/qwen3asr`) listens on :8000 and Kokoro on :8880 (host network).
  The ASR returns "Ahora." for pure silence, so that transcript means "the audio was zeros".
