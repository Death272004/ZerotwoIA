# ZeroTwoIA/config.py

MODEL_NAME = "mistral"

MODEL_OPTIONS = {
    "temperature": 0.8,
    "top_p": 0.9,
    "num_ctx": 2048
}

MAX_HISTORY = 8
MAX_DB_ROWS = 500

# Si está en True, usa Ollama para clasificar mensajes ambiguos antes de responder.
# Es más preciso para detectar herramientas, pero añade una llamada extra al modelo.
ENABLE_LLM_INTENT_FALLBACK = False

# Rutas de aplicaciones — edita aquí si cambias de PC
APPS = {
    "chrome":   r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad":  "notepad.exe",
    "vscode":   r"C:\Users\rrpin\AppData\Local\Programs\Microsoft VS Code\Code.exe"
}
