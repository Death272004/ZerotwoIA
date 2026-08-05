# ZeroTwoIA/config.py

MODEL_NAME = "mistral"

MODEL_OPTIONS = {
    "temperature": 0.8,
    "top_p": 0.9,
    "num_ctx": 4096
}

MAX_HISTORY = 20
MAX_DB_ROWS = 500

# Rutas de aplicaciones — edita aquí si cambias de PC
APPS = {
    "chrome":   r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad":  "notepad.exe",
    "vscode":   r"C:\Users\rrpin\AppData\Local\Programs\Microsoft VS Code\Code.exe"
}
