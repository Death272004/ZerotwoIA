# ZeroTwoIA/config.py

import os

MODEL_NAME = os.getenv("ZEROTWO_MODEL", "llama3.2:1b")

MODEL_OPTIONS = {
    "temperature": 0.82,
    "top_p": 0.85,
    "num_ctx": 1024,
    "num_predict": 90,
}

MAX_HISTORY = 4
MAX_DB_ROWS = 500

# Si está en True, usa Ollama para clasificar mensajes ambiguos antes de responder.
# Es más preciso para detectar herramientas, pero añade una llamada extra al modelo.
ENABLE_LLM_INTENT_FALLBACK = False

# Voz de ZeroTwo.
# No clona a ninguna actriz real; usa una voz neural latina con ajustes de tono.
TTS_VOICE = os.getenv("ZEROTWO_VOICE", "es-MX-DaliaNeural")
TTS_RATE = os.getenv("ZEROTWO_VOICE_RATE", "+8%")
TTS_PITCH = os.getenv("ZEROTWO_VOICE_PITCH", "+12Hz")

# Rutas de aplicaciones — edita aquí si cambias de PC
APPS = {
    "chrome":   r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad":  "notepad.exe",
    "vscode":   r"C:\Users\rrpin\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "calculadora": "calc.exe",
}
