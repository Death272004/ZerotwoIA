# tools/app_launcher.py

import subprocess
from config import APPS


def open_app(name: str) -> str:
    if name not in APPS:
        return f"Aplicación '{name}' no registrada"

    try:
        subprocess.Popen(APPS[name])
        return f"Abriendo {name}"
    except Exception as e:
        return f"Error al abrir {name}: {e}"
