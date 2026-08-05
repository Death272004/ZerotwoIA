# core/intent.py

import re
import ollama  # type: ignore
from config import ENABLE_LLM_INTENT_FALLBACK, MODEL_NAME

# Patrones rápidos — se evalúan antes de llamar al LLM
_PATTERNS = {
    "system": re.compile(
        r"\b(abre?|abrir|lanza?|lanzar|ejecuta?|ejecutar|inicia?|iniciar)\b.{0,30}"
        r"\b(chrome|firefox|notepad|vscode|visual studio|bloc de notas|calculadora)\b",
        re.IGNORECASE
    ),
    "web": re.compile(
        r"\b(busca?|buscar|googlea?|googlear|busca en internet|busca en la web|"
        r"qué es|quién es|cómo se hace|información sobre)\b",
        re.IGNORECASE
    ),
    "code": re.compile(
        r"\b(escribe?|escribir|genera?|generar|crea?|crear|arregla?|arreglar|"
        r"corrige?|corregir|explica?|explicar)\b.{0,20}"
        r"\b(código|función|script|clase|método|programa|bug|error)\b",
        re.IGNORECASE
    ),
}

# Extrae el nombre de app mencionado
_APP_NAMES = re.compile(
    r"\b(chrome|firefox|notepad|vscode|visual studio|bloc de notas|calculadora)\b",
    re.IGNORECASE
)

_APP_ALIASES = {
    "visual studio": "vscode",
    "bloc de notas": "notepad",
}


def _extract_target(text: str) -> str:
    match = _APP_NAMES.search(text)
    if not match:
        return ""
    name = match.group(0).lower()
    return _APP_ALIASES.get(name, name)


def _llm_fallback(text: str) -> dict:
    """Usa Mistral para clasificar cuando los regex no son suficientes."""
    prompt = (
        "Clasifica el siguiente mensaje en UNA de estas categorías: "
        "system, web, code, chat.\n"
        "Responde SOLO con la palabra en minúsculas, sin explicación.\n\n"
        f"Mensaje: {text}"
    )
    try:
        resp = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0, "num_ctx": 256}
        )
        intent_type = resp["message"]["content"].strip().lower()
        if intent_type not in ("system", "web", "code", "chat"):
            intent_type = "chat"
    except Exception:
        intent_type = "chat"

    return {"type": intent_type, "raw": text}


def detect_intent(text: str) -> dict:
    """
    Retorna un dict con al menos {"type": ..., "raw": text}.
    Para type="system" añade {"action": "open_app", "target": <app>}.
    Para type="web"    añade {"query": text}.
    Para type="code"   añade {"task": text}.
    """
    for intent_type, pattern in _PATTERNS.items():
        if pattern.search(text):
            if intent_type == "system":
                return {
                    "type": "system",
                    "action": "open_app",
                    "target": _extract_target(text),
                    "raw": text,
                }
            if intent_type == "web":
                return {"type": "web", "query": text, "raw": text}
            if intent_type == "code":
                return {"type": "code", "task": text, "raw": text}

    if ENABLE_LLM_INTENT_FALLBACK:
        return _llm_fallback(text)

    return {"type": "chat", "raw": text}
