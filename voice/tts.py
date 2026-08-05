# voice/tts.py

import asyncio
import os
import winsound
from edge_tts import Communicate


def speak(text: str, output_path: str = "data/response.wav", language: str = "es") -> str:
    """
    Sintetiza texto con edge-tts (rápido, ~1-2 segundos).
    Retorna la ruta del archivo generado.
    """
    if not text.strip():
        return ""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    async def _tts():
        communicate = Communicate(text, "es-AR-ElenaNeural")
        await communicate.save(output_path)

    try:
        asyncio.run(_tts())
    except Exception as e:
        return ""
    
    return output_path if os.path.exists(output_path) else ""


def speak_and_play(text: str, language: str = "es"):
    """Sintetiza el texto y lo reproduce."""
    path = speak(text, language=language)
    if not path:
        return

    # Reproduce con winsound nativo (no bloqueante)
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass  # Si falla, continúa silenciosamente
