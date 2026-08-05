from functools import lru_cache
import threading
from time import perf_counter

from core.intent import detect_intent
from core.core_brain import enviar_mensaje_streaming
from agents.system_agent import execute_command
from agents.web_agent import handle as web_handle
from agents.code_agent import handle as code_handle


@lru_cache(maxsize=128)
def _cached_intent(text: str) -> tuple:
    return tuple(sorted(detect_intent(text).items()))


def execute_action(action: dict) -> None:
    """Ejecuta la acción que ZeroTwo indicó en su respuesta."""
    t = action.get("type")
    if t == "open_app":
        execute_command(action)
    elif t == "web_search":
        query = action.get("query", "")
        web_handle({"type": "web", "query": query, "raw": query})
    elif t == "open_url":
        target = action.get("target", "")
        web_handle({"type": "web", "query": target, "raw": target})
    elif t == "youtube":
        query = action.get("query", "")
        web_handle({"type": "web", "query": "youtube " + query, "raw": query})


def tts_background(text: str) -> None:
    """Ejecuta TTS en background sin bloquear la UI."""
    from voice.tts import speak_and_play
    try:
        speak_and_play(text)
    except Exception:
        pass


def _say_tool_result(result: str) -> None:
    print(f"ZeroTwo: {result}")
    threading.Thread(target=tts_background, args=(result,), daemon=True).start()


def _record_voice_once(duration: int = 6) -> str:
    """Graba una sola toma de voz y retorna el texto transcrito."""
    from voice.stt import grabar_audio, transcribir
    from voice.tts import is_playing, stop_playback

    if is_playing():
        print("  Deteniendo voz antes de abrir el microfono...")
        stop_playback()

    path = grabar_audio(duracion=duration)
    print("  Procesando voz...")
    text = transcribir(path).strip()
    if text:
        print(f"  Entendi: {text}")
    else:
        print("  No detecte voz clara. Escribe o di 'voz' para intentar otra vez.\n")
    return text


def responder_con_streaming(user_input: str) -> None:
    """
    Responde con streaming: muestra texto INMEDIATAMENTE mientras se genera,
    y ejecuta TTS en background para no bloquear.
    """
    started_at = perf_counter()

    # Detectar intención rápido
    intent = dict(_cached_intent(user_input))
    intent_done_at = perf_counter()

    intent_type = intent.get("type")
    if intent_type == "system":
        _say_tool_result(execute_command(intent))
        print(f"⏱ intención: {intent_done_at - started_at:.2f}s | total: {perf_counter() - started_at:.2f}s")
        return
    if intent_type == "web":
        _say_tool_result(web_handle(intent))
        print(f"⏱ intención: {intent_done_at - started_at:.2f}s | total: {perf_counter() - started_at:.2f}s")
        return
    if intent_type == "code":
        _say_tool_result(code_handle(intent))
        print(f"⏱ intención: {intent_done_at - started_at:.2f}s | total: {perf_counter() - started_at:.2f}s")
        return
    
    # Para conversación: usar streaming
    print("ZeroTwo: ", end="", flush=True)  # Mostrar "ZeroTwo:" al instante
    first_chunk_at = None
    
    def on_chunk(chunk):
        """Callback para cada chunk recibido."""
        nonlocal first_chunk_at
        if first_chunk_at is None:
            first_chunk_at = perf_counter()
        print(chunk, end="", flush=True)  # Mostrar en tiempo real
    
    texto, accion = enviar_mensaje_streaming(user_input, callback=on_chunk)
    response_done_at = perf_counter()
    print()  # Nueva línea al final
    first_text = (first_chunk_at or response_done_at) - started_at
    print(
        "⏱ "
        f"intención: {intent_done_at - started_at:.2f}s | "
        f"primer texto: {first_text:.2f}s | "
        f"respuesta: {response_done_at - started_at:.2f}s"
    )
    
    if accion:
        threading.Thread(target=execute_action, args=(accion,), daemon=True).start()
    
    # Ejecutar TTS en background (no bloqueante)
    threading.Thread(target=tts_background, args=(texto,), daemon=True).start()


def loop_texto() -> None:
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


def loop_híbrido() -> None:
    """
    Modo unificado: 
    - "voz" / "audio" / Enter vacio -> graba una sola toma de voz
    - Escribir texto + Enter → usa el texto
    - "salir" -> cierra el asistente
    - ZeroTwo responde en texto y voz en background
    """
    print("ZeroTwo: En línea. [modo híbrido - voz + texto]")
    print("  Escribe texto = chat | voz/audio o Enter vacio = microfono | salir = cerrar\n")

    while True:
        try:
            user_input = input("Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nZeroTwo: Hasta la próxima.")
            break

        command = user_input.lower()
        if command in {"salir", "exit", "quit", "cerrar"}:
            print("ZeroTwo: Hasta la próxima.")
            break

        # Si pidio voz, graba una sola toma. No queda en modo escucha continua.
        if not user_input or command in {"voz", "audio", "microfono", "mic"}:
            try:
                user_input = _record_voice_once(duration=6)
                if not user_input:
                    continue
            except KeyboardInterrupt:
                print("\n  Cancelado")
                continue
            except Exception as e:
                print(f"  Error de microfono: {e}\n")
                continue

        # Procesa la entrada con streaming (voz o texto)
        try:
            responder_con_streaming(user_input)
        except Exception as e:
            print(f"ZeroTwo: Algo falló — {e}")


if __name__ == "__main__":
    loop_híbrido()
