# core/core_brain.py

import re
import threading
import ollama  # type: ignore
from core.personality import SYSTEM_PROMPT
from core.memory import save_message, load_history, init_db
from config import MODEL_NAME, MODEL_OPTIONS, MAX_HISTORY

init_db()

historial = [{"role": "system", "content": SYSTEM_PROMPT}]
historial += load_history(MAX_HISTORY)

# Detecta tags de acción al final de la respuesta
_ACTION_TAG = re.compile(r'\[ACTION:(\w+):([^\]]+)\]\s*$')

# Para streaming
_streaming_response = ""


def parse_action(text: str) -> tuple:
    """
    Extrae el tag de acción del texto si existe.
    Retorna (texto_limpio, accion_dict | None)
    """
    match = _ACTION_TAG.search(text)
    if not match:
        return text.strip(), None

    action_type  = match.group(1).strip()
    action_value = match.group(2).strip()
    clean_text   = _ACTION_TAG.sub('', text).strip()

    return clean_text, {
        "type":   action_type,
        "action": action_type,
        "target": action_value,
        "query":  action_value,
    }


def enviar_mensaje(mensaje_usuario: str) -> tuple:
    """
    Retorna (texto_respuesta, accion | None).
    Usa streaming para respuesta más rápida.
    """
    global historial

    historial.append({"role": "user", "content": mensaje_usuario})
    save_message("user", mensaje_usuario)

    contexto = [historial[0]] + historial[-(MAX_HISTORY):]

    try:
        # Streaming para respuesta progresiva
        contenido = ""
        for chunk in ollama.chat(
            model=MODEL_NAME,
            messages=contexto,
            options=MODEL_OPTIONS,
            stream=True  # IMPORTANTE: streaming habilitado
        ):
            if "message" in chunk:
                contenido += chunk["message"]["content"]
        
        if not contenido:
            raise Exception("Respuesta vacía")
            
    except Exception as e:
        historial.pop()
        error_str = str(e)
        if "connection" in error_str.lower():
            texto_limpio = "No puedo conectar con Ollama. ¿Está corriendo 'ollama serve'?"
        elif "timeout" in error_str.lower():
            texto_limpio = "Ollama está tardando demasiado. Intenta de nuevo."
        else:
            texto_limpio = f"Error: {error_str[:80]}"
        return texto_limpio, None

    texto_limpio, accion = parse_action(contenido)

    historial.append({"role": "assistant", "content": texto_limpio})
    save_message("assistant", texto_limpio)

    if len(historial) > MAX_HISTORY + 1:
        historial = [historial[0]] + historial[-(MAX_HISTORY):]

    return texto_limpio, accion


def enviar_mensaje_streaming(mensaje_usuario: str, callback=None) -> tuple:
    """
    Versión con streaming: llama callback() con cada chunk para UI reactiva.
    callback(chunk_text) es llamado mientras se genera la respuesta.
    
    Retorna (texto_completo, accion | None).
    """
    global historial

    historial.append({"role": "user", "content": mensaje_usuario})
    save_message("user", mensaje_usuario)

    contexto = [historial[0]] + historial[-(MAX_HISTORY):]

    try:
        contenido = ""
        for chunk in ollama.chat(
            model=MODEL_NAME,
            messages=contexto,
            options=MODEL_OPTIONS,
            stream=True
        ):
            if "message" in chunk:
                delta = chunk["message"]["content"]
                contenido += delta
                if callback:
                    callback(delta)  # Actualizar UI con cada palabra/chunk
        
        if not contenido:
            raise Exception("Respuesta vacía")
            
    except Exception as e:
        historial.pop()
        error_str = str(e)
        if "connection" in error_str.lower():
            texto_limpio = "No puedo conectar con Ollama. ¿Está corriendo 'ollama serve'?"
        elif "timeout" in error_str.lower():
            texto_limpio = "Ollama está tardando demasiado. Intenta de nuevo."
        else:
            texto_limpio = f"Error: {error_str[:80]}"
        if callback:
            callback(texto_limpio)
        return texto_limpio, None

    texto_limpio, accion = parse_action(contenido)

    historial.append({"role": "assistant", "content": texto_limpio})
    save_message("assistant", texto_limpio)

    if len(historial) > MAX_HISTORY + 1:
        historial = [historial[0]] + historial[-(MAX_HISTORY):]

    return texto_limpio, accion
