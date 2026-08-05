# voice/stt.py

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import threading

# Carga lazy — el modelo solo se inicializa la primera vez que se usa
_model = None
_transcription_timeout = 30  # segundos máximo de espera

def get_model() -> WhisperModel:
    global _model
    if _model is None:
        # device="cpu" + int8 = óptimo para AMD Ryzen sin CUDA
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def _detectar_silencio(path: str, threshold: float = 0.01) -> bool:
    """Detecta si el archivo de audio es principalmente silencio."""
    try:
        from scipy.io.wavfile import read
        fs, audio = read(path)
        # Normalizar
        audio = audio.astype(np.float32) / (np.max(np.abs(audio)) + 1e-9)
        # Si el promedio de amplitud es bajo, es silencio
        return np.mean(np.abs(audio)) < threshold
    except:
        return False


def grabar_audio(path: str = "audio.wav", duracion: int = 5, fs: int = 16000) -> str:
    """Graba audio del micrófono. fs=16000 es lo que Whisper espera nativamente."""
    print(f"  🎤 Grabando durante {duracion} segundos...")
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1)
    sd.wait()
    write(path, fs, audio)
    return path


def transcribir(path: str) -> str:
    """Transcribe audio a texto con timeout y detección de silencio."""
    
    # Detectar silencio antes de procesar
    if _detectar_silencio(path):
        return ""
    
    resultado = {"texto": ""}
    error = {"msg": ""}
    
    def _transcribe_worker():
        try:
            segmentos, _ = get_model().transcribe(
                path,
                language="es",  # Optimizar para español
            )
            # Extraer texto de segmentos
            textos = []
            for s in segmentos:
                if hasattr(s, 'text'):
                    texto = s.text.strip()
                    if texto:
                        textos.append(texto)
            resultado["texto"] = " ".join(textos).strip()
        except Exception as e:
            error["msg"] = str(e)
    
    # Ejecutar con timeout
    thread = threading.Thread(target=_transcribe_worker, daemon=True)
    thread.start()
    thread.join(timeout=_transcription_timeout)
    
    if thread.is_alive():
        return ""  # Timeout
    
    if error["msg"]:
        return ""
    
    return resultado["texto"]
