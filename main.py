# main.py

from functools import lru_cache
import threading
from io import StringIO
import sys

from core.intent import detect_intent
from core.core_brain import enviar_mensaje, enviar_mensaje_streaming
from agents.system_agent import execute_command
from agents.web_agent import handle as web_handle
from agents.code_agent import handle as code_handle


@lru_cache(maxsize=128)
def _cached_intent(text: str) -> tuple:
    return tuple(sorted(detect_intent(text).items()))


def execute_action(action: dict):
    """Ejecuta la acción que ZeroTwo indicó en su respuesta."""
    t = action.get("type")
    if t == "open_app":
        execute_command(action)
    elif t == "web_search":
        web_handle({"type": "web", "query": action.get("query", ""), "raw": action.get("query", "")})
    elif t == "open_url":
        web_handle({"type": "web", "query": action.get("target", ""), "raw": action.get("target", "")})
    elif t == "youtube":
        web_handle({"type": "web", "query": "youtube " + action.get("query", ""), "raw": action.get("query", "")})


def tts_background(text: str):
    """Ejecuta TTS en background sin bloquear la UI."""
    from voice.tts import speak_and_play
    try:
        speak_and_play(text)
    except Exception:
        pass  # Falla silenciosa


def responder_con_streaming(user_input: str):
    """
    Responde con streaming: muestra texto INMEDIATAMENTE mientras se genera,
    y ejecuta TTS en background para no bloquear.
    """
    from voice.tts import speak_and_play
    
    # Detectar intención rápido
    intent = dict(_cached_intent(user_input))
    
    if intent["type"] == "system":
        result = execute_command(intent)
        print(f"ZeroTwo: {result}")
        threading.Thread(target=tts_background, args=(result,), daemon=True).start()
        return
    if intent["type"] == "web":
        result = web_handle(intent)
        print(f"ZeroTwo: {result}")
        threading.Thread(target=tts_background, args=(result,), daemon=True).start()
        return
    if intent["type"] == "code":
        result = code_handle(intent)
        print(f"ZeroTwo: {result}")
        threading.Thread(target=tts_background, args=(result,), daemon=True).start()
        return
    
    # Para conversación: usar streaming
    print("ZeroTwo: ", end="", flush=True)  # Mostrar "ZeroTwo:" al instante
    
    respuesta_buffer = []
    
    def on_chunk(chunk):
        """Callback para cada chunk recibido."""
        respuesta_buffer.append(chunk)
        print(chunk, end="", flush=True)  # Mostrar en tiempo real
    
    texto, accion = enviar_mensaje_streaming(user_input, callback=on_chunk)
    print()  # Nueva línea al final
    
    if accion:
        threading.Thread(target=execute_action, args=(accion,), daemon=True).start()
    
    # Ejecutar TTS en background (no bloqueante)
    threading.Thread(target=tts_background, args=(texto,), daemon=True).start()


def loop_texto():
    print("ZeroTwo: En línea. [modo texto]")
    while True:
        try:
            user_input = input("Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nZeroTwo: Hasta la próxima.")
            break

        if not user_input:
            continue

        try:
            responder_con_streaming(user_input)
        except Exception as e:
            print(f"ZeroTwo: Algo falló — {e}")


def loop_híbrido():
    """
    Modo unificado: 
    - Enter vacío → graba voz (6 seg)
    - Escribir texto + Enter → usa el texto
    - ZeroTwo responde INMEDIATAMENTE en texto + voz en background
    """
    from voice.stt import grabar_audio, transcribir

    print("ZeroTwo: En línea. [modo híbrido - voz + texto]")
    print("  Enter vacío = micrófono | Escribe algo = texto\n")

    while True:
        try:
            user_input = input("Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nZeroTwo: Hasta la próxima.")
            break

        # Si presionó Enter vacío, graba voz
        if not user_input:
            try:
                path = grabar_audio(duracion=6)
                print("  ⏳ Procesando voz (puede tardar unos segundos)...")
                user_input = transcribir(path).strip()
                if user_input:
                    print(f"  ✓ Entendí: {user_input}")
                else:
                    print("  ✗ No detecté voz clara, intenta de nuevo\n")
                    continue
            except KeyboardInterrupt:
                print("\n  ⏹ Cancelado")
                continue
            except Exception as e:
                print(f"  ✗ Error de micrófono: {e}\n")
                continue

        # Procesa la entrada con streaming (voz o texto)
        try:
            responder_con_streaming(user_input)
        except Exception as e:
            print(f"ZeroTwo: Algo falló — {e}")


if __name__ == "__main__":
    loop_híbrido()
