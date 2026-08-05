# agents/code_agent.py

import ollama  # type: ignore
from config import MODEL_NAME, MODEL_OPTIONS

_CODE_SYSTEM = """
Eres un asistente experto en programación.
Cuando el usuario te pida código, responde SOLO con el código limpio y un comentario breve si es necesario.
Cuando te pidan explicar algo, sé directo y técnico.
No añades introducción ni conclusión innecesaria.
"""


def handle(intent: dict) -> str:
    """
    Recibe un intent de tipo "code" y responde usando Mistral
    con un system prompt especializado en programación.
    """
    task = intent.get("task") or intent.get("raw", "")

    if not task:
        return "No especificaste qué necesitas con el código."

    messages = [
        {"role": "system", "content": _CODE_SYSTEM},
        {"role": "user",   "content": task},
    ]

    try:
        resp = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            options={**MODEL_OPTIONS, "temperature": 0.3},  # más determinista para código
        )
        return resp["message"]["content"]
    except Exception as e:
        return f"Error al generar código: {e}"
