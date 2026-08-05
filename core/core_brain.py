import re
import ollama  # type: ignore
from core.personality import SYSTEM_PROMPT
from core.memory import save_message, load_history, init_db
from config import MODEL_NAME, MODEL_OPTIONS, MAX_HISTORY

init_db()

historial = [{"role": "system", "content": SYSTEM_PROMPT}]
historial += load_history(MAX_HISTORY)

# Detecta tags de acción al final de la respuesta
_ACTION_TAG = re.compile(r'\[ACTION:(\w+):([^\]]+)\]\s*$')

def parse_action(text: str) -> tuple[str, dict | None]:
    """
    Extrae el tag de acción del texto si existe.
    Retorna (texto_limpio, accion_dict | None)
    """
    match = _ACTION_TAG.search(text)
    if not match:
        return text.strip(), None

    action_type = match.group(1).strip()
    action_value = match.group(2).strip()
    clean_text = _ACTION_TAG.sub('', text).strip()

    return clean_text, {
        "type": action_type,
        "action": action_type,
        "target": action_value,
        "query": action_value,
    }


def _build_context() -> list[dict]:
    return [historial[0]] + historial[-MAX_HISTORY:]


def _format_ollama_error(error: Exception) -> str:
    error_str = str(error)
    if "connection" in error_str.lower():
        return "No puedo conectar con Ollama. ¿Está corriendo 'ollama serve'?"
    if "timeout" in error_str.lower():
        return "Ollama está tardando demasiado. Intenta de nuevo."
    return f"Error: {error_str[:80]}"


def _trim_history() -> None:
    global historial
    if len(historial) > MAX_HISTORY + 1:
        historial = [historial[0]] + historial[-MAX_HISTORY:]


def _chat_stream(callback=None) -> str:
    contenido = ""
    for chunk in ollama.chat(
        model=MODEL_NAME,
        messages=_build_context(),
        options=MODEL_OPTIONS,
        stream=True,
    ):
        delta = chunk.get("message", {}).get("content", "")
        if not delta:
            continue
        contenido += delta
        if callback:
            callback(delta)

    if not contenido:
        raise RuntimeError("Respuesta vacía")

    return contenido


def enviar_mensaje(mensaje_usuario: str) -> tuple[str, dict | None]:
    """
    Retorna (texto_respuesta, accion | None).
    Usa streaming para respuesta más rápida.
    """
    return enviar_mensaje_streaming(mensaje_usuario)


def enviar_mensaje_streaming(mensaje_usuario: str, callback=None) -> tuple[str, dict | None]:
    """
    Versión con streaming: llama callback() con cada chunk para UI reactiva.
    callback(chunk_text) es llamado mientras se genera la respuesta.
    
    Retorna (texto_completo, accion | None).
    """
    global historial

    historial.append({"role": "user", "content": mensaje_usuario})
    save_message("user", mensaje_usuario)

    try:
        contenido = _chat_stream(callback)
    except Exception as e:
        historial.pop()
        texto_limpio = _format_ollama_error(e)
        if callback:
            callback(texto_limpio)
        return texto_limpio, None

    texto_limpio, accion = parse_action(contenido)

    historial.append({"role": "assistant", "content": texto_limpio})
    save_message("assistant", texto_limpio)
    _trim_history()

    return texto_limpio, accion
