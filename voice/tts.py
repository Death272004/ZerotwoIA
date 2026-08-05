import asyncio
import threading
from pathlib import Path
from edge_tts import Communicate

try:
    import winsound
except ImportError:  # winsound solo existe en Windows.
    winsound = None

VOICE_BY_LANGUAGE = {
    "es": "es-AR-ElenaNeural",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_playback_active = threading.Event()


def is_playing() -> bool:
    """Indica si el reproductor de voz sigue hablando."""
    return _playback_active.is_set()


def stop_playback() -> None:
    """Detiene la voz actual antes de abrir el microfono."""
    if winsound is None:
        _playback_active.clear()
        return

    try:
        winsound.PlaySound(None, 0)
    except Exception:
        pass
    finally:
        _playback_active.clear()


def speak(text: str, output_path: str = "data/response.wav", language: str = "es") -> str:
    """
    Sintetiza texto con edge-tts (rápido, ~1-2 segundos).
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
        communicate = Communicate(text, voice)
        await communicate.save(str(output_file))

    try:
        asyncio.run(_tts())
    except Exception:
        return ""

    return str(output_file) if output_file.exists() else ""


def speak_and_play(text: str, language: str = "es") -> None:
    """Sintetiza el texto y lo reproduce."""
    path = speak(text, language=language)
    if not path or winsound is None:
        return

    # Esta funcion ya corre en un thread de fondo; reproducir en modo bloqueante
    # permite saber cuando termino y evita que el microfono capture la propia voz.
    try:
        _playback_active.set()
        winsound.PlaySound(path, winsound.SND_FILENAME)
    except Exception:
        pass  # Si falla, continúa silenciosamente
    finally:
        _playback_active.clear()
