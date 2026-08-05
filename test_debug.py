#!/usr/bin/env python
# Test para diagnosticar dónde está el cuello de botella

import time

print("[1] Importando módulos...")
t = time.time()
from core.intent import detect_intent
print(f"  ✓ intent.py — {time.time()-t:.2f}s")

t = time.time()
from core.core_brain import enviar_mensaje
print(f"  ✓ core_brain.py — {time.time()-t:.2f}s")

t = time.time()
from voice.tts import speak_and_play
print(f"  ✓ tts.py — {time.time()-t:.2f}s")

print("\n[2] Probando detect_intent...")
t = time.time()
intent = detect_intent("hola")
print(f"  ✓ detect_intent — {time.time()-t:.2f}s")
print(f"    Resultado: {intent}")

print("\n[3] Probando enviar_mensaje...")
t = time.time()
texto, accion = enviar_mensaje("hola")
print(f"  ✓ enviar_mensaje — {time.time()-t:.2f}s")
print(f"    Respuesta: {texto[:50]}...")

print("\n[4] Probando TTS...")
t = time.time()
speak_and_play("Prueba de audio")
print(f"  ✓ TTS — {time.time()-t:.2f}s")

print("\n✅ Todo OK")
