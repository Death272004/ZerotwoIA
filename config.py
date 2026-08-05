# ZeroTwoIA/config.py

import os

MODEL_NAME = os.getenv("ZEROTWO_MODEL", "llama3.2:1b")

MODEL_OPTIONS = {
    "temperature": 0.7,
    "top_p": 0.85,
    "num_ctx": 1024,
    "num_predict": 120,
}

MAX_HISTORY = 4
MAX_DB_ROWS = 500

# Si está en True, usa Ollama para clasificar mensajes ambiguos antes de responder.
# Es más preciso para detectar herramientas, pero añade una llamada extra al modelo.
ENABLE_LLM_INTENT_FALLBACK = False

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
