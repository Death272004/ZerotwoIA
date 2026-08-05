import asyncio
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

    # Reproduce con winsound nativo (no bloqueante)
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass  # Si falla, continúa silenciosamente
