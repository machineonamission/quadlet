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

## Pins / gotchas
- **LVA (`*/smarthome/lva/linux-voice-assistant.container`) is pinned to a digest**, the
  2026-11-25 nightly (commit `9ab4b17`), with AutoUpdate off. Later nightlies made both
  satellites stream silence to HA after the wake word: Qwen3-ASR transcribes digital silence as
  "Ahora.". Suspects are aioesphomeapi 46.30.1 (#570) and the remote-mute changes (#489/#622).
  Unpin once upstream is fixed. Stable `1.1.18` lacks `SENDSPIN_URL`/`VOLUME_CONTROLLER`.
- Qwen3-ASR (`smarthome/qwen3asr`) listens on :8000 and Kokoro on :8880 (host network).
