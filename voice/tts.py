import asyncio
import json
import os
import threading
import time
from pathlib import Path
from edge_tts import Communicate
from config import TTS_PITCH, TTS_PRESET, TTS_RATE, TTS_VOICE, VOICE_PRESETS

try:
    import pygame
except ImportError:
    pygame = None

VOICE_BY_LANGUAGE = {
    "es": TTS_VOICE,
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VOICE_CONFIG_PATH = PROJECT_ROOT / "data" / "voice_config.json"
_playback_active = threading.Event()
_voice_lock = threading.Lock()
_active_preset_id = None
_pygame_ready = False


def _preset_by_id(preset_id: str) -> dict:
    for preset in VOICE_PRESETS:
        if preset["id"] == preset_id:
            return preset
    return VOICE_PRESETS[0]


def _load_preset_id() -> str:
    try:
        if VOICE_CONFIG_PATH.exists():
            data = json.loads(VOICE_CONFIG_PATH.read_text(encoding="utf-8"))
            return data.get("preset_id") or TTS_PRESET
    except Exception:
        pass
    return TTS_PRESET


def _save_preset_id(preset_id: str) -> None:
    VOICE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    VOICE_CONFIG_PATH.write_text(json.dumps({"preset_id": preset_id}, indent=2), encoding="utf-8")


def get_voice_presets() -> list[dict]:
    """Devuelve las voces disponibles para la interfaz."""
    return [dict(preset) for preset in VOICE_PRESETS]


def get_voice_preset() -> dict:
    """Devuelve la voz activa, leyendo la preferencia guardada una sola vez."""
    global _active_preset_id
    with _voice_lock:
        if _active_preset_id is None:
            _active_preset_id = _load_preset_id()
        return dict(_preset_by_id(_active_preset_id))


def set_voice_preset(preset_id: str, persist: bool = True) -> dict:
    """Cambia la voz activa para las siguientes respuestas."""
    global _active_preset_id
    preset = _preset_by_id(preset_id)
    with _voice_lock:
        _active_preset_id = preset["id"]
        if persist:
            _save_preset_id(_active_preset_id)
    return dict(preset)


def cycle_voice_preset() -> dict:
    """Avanza a la siguiente voz disponible."""
    current = get_voice_preset()["id"]
    ids = [preset["id"] for preset in VOICE_PRESETS]
    next_index = (ids.index(current) + 1) % len(ids) if current in ids else 0
    return set_voice_preset(ids[next_index])


def is_playing() -> bool:
    """Indica si el reproductor de voz sigue hablando."""
    return _playback_active.is_set()


def stop_playback() -> None:
    """Detiene la voz actual antes de abrir el microfono."""
    _playback_active.clear()
    if pygame is None:
        return
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass


def speak(text: str, output_path: str = "data/response.mp3", language: str = "es") -> str:
    """
    Sintetiza texto con edge-tts.
    Retorna la ruta del archivo generado.
    """
    if not text.strip():
        return ""

    output_file = Path(output_path)
    if not output_file.is_absolute():
        output_file = PROJECT_ROOT / output_file
    output_file.parent.mkdir(parents=True, exist_ok=True)

    async def _tts():
        preset = get_voice_preset()
        voice = preset.get("voice") or VOICE_BY_LANGUAGE.get(language, VOICE_BY_LANGUAGE["es"])
        rate = preset.get("rate") or TTS_RATE
        pitch = preset.get("pitch") or TTS_PITCH
        communicate = Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(str(output_file))

    try:
        asyncio.run(_tts())
    except Exception as exc:
        print(f"\n  Voz: no pude generar audio ({exc})")
        return ""

    return str(output_file) if output_file.exists() else ""


def _init_player() -> bool:
    """Inicializa pygame.mixer una sola vez."""
    global _pygame_ready
    if pygame is None:
        return False
    if _pygame_ready and pygame.mixer.get_init():
        return True

    try:
        pygame.mixer.init()
        _pygame_ready = True
        return True
    except Exception as exc:
        print(f"\n  Voz: no pude inicializar el reproductor ({exc})")
        return False


def _play_with_default_app(path: str) -> bool:
    """Ultimo recurso en Windows si pygame no esta instalado."""
    if os.name != "nt" or not hasattr(os, "startfile"):
        return False
    try:
        os.startfile(path)
        return True
    except Exception:
        return False


def speak_and_play(text: str, language: str = "es") -> None:
    """Sintetiza el texto y lo reproduce."""
    path = speak(text, language=language)
    if not path:
        return

    if not _init_player():
        if not _play_with_default_app(path):
            print("\n  Voz: instala pygame o revisa la salida de audio.")
        return

    try:
        _playback_active.set()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

        while _playback_active.is_set() and pygame.mixer.music.get_busy():
            time.sleep(0.05)

        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.unload()
        except Exception:
            pass
    except Exception as exc:
        print(f"\n  Voz: no pude reproducir audio ({exc})")
    finally:
        _playback_active.clear()
