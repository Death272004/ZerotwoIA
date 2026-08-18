import asyncio
import os
import threading
import time
from pathlib import Path
from edge_tts import Communicate
from config import TTS_PITCH, TTS_RATE, TTS_VOICE

try:
    import pygame
except ImportError:
    pygame = None

VOICE_BY_LANGUAGE = {
    "es": TTS_VOICE,
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_playback_active = threading.Event()
_pygame_ready = False


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
        voice = VOICE_BY_LANGUAGE.get(language, VOICE_BY_LANGUAGE["es"])
        communicate = Communicate(text, voice, rate=TTS_RATE, pitch=TTS_PITCH)
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
