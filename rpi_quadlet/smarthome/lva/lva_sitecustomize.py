# Mounted into the linux-voice-assistant container as /app/patches/sitecustomize.py
# (PYTHONPATH=/app/patches), so Python runs it before LVA imports anything.
#
# Why: Home Assistant 2026.12 (core PR #190096, "Pass ESPHome device audio settings
# to the pipeline") multiplies the satellite's audio by the `volume_multiplier` the
# device sends in VoiceAssistantRequest.audio_settings. ESPHome firmware sends 1.0.
# LVA sends no audio_settings at all, so HA reads protobuf's default 0.0 and every
# chunk becomes digital silence; Qwen3-ASR then transcribes it as "Ahora.".
#
# Fix: make every VoiceAssistantRequest LVA builds carry volume_multiplier=1.0
# (noise_suppression_level / auto_gain stay 0 = HA defaults). LVA only constructs
# these messages (no isinstance checks), and aioesphomeapi's MESSAGE_TYPE_TO_PROTO
# keeps the real class, so a factory returning real instances is safe.
#
# Remove once HA or LVA fixes it upstream. Kept in sync with
# rpi_quadlet/smarthome/lva/lva_sitecustomize.py (server) / quadlet/... (Pi): keep both identical.
import logging

try:
    from aioesphomeapi import api_pb2 as _pb

    _RealVoiceAssistantRequest = _pb.VoiceAssistantRequest

    def _voice_assistant_request(*args, **kwargs):
        msg = _RealVoiceAssistantRequest(*args, **kwargs)
        if msg.start and not msg.HasField("audio_settings"):
            msg.audio_settings.volume_multiplier = 1.0
        return msg

    _pb.VoiceAssistantRequest = _voice_assistant_request
    logging.getLogger("lva_sitecustomize").warning(
        "Patched VoiceAssistantRequest: audio_settings.volume_multiplier defaults to 1.0"
    )
except Exception:  # never stop LVA from starting
    logging.getLogger("lva_sitecustomize").exception("VoiceAssistantRequest patch failed")
