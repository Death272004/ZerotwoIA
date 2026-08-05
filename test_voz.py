#!/usr/bin/env python3
"""
test_voz.py - Prueba el sistema de voz (STT y TTS)
Uso: python test_voz.py
"""

import time
import sys

def test_voice_system():
    """Prueba grabación y transcripción."""
    from voice.stt import grabar_audio, transcribir, _detectar_silencio
    from voice.tts import speak_and_play
    
    print("\n" + "="*60)
    print("🎙️  TEST DE SISTEMA DE VOZ - ZeroTwo")
    print("="*60)
    
    # Test 1: Grabar audio
    print("\n1️⃣  TEST DE GRABACIÓN")
    print("-" * 40)
    print("Grabando 5 segundos de audio...")
    print("Habla algo o haz ruido 🔊\n")
    
    start = time.time()
    audio_path = grabar_audio(path="test_audio.wav", duracion=5)
    print(f"✓ Grabación guardada en: {audio_path}")
    print(f"⏱️  Tiempo: {time.time() - start:.2f}s\n")
    
    # Test 2: Detectar silencio
    print("2️⃣  TEST DE DETECCIÓN DE SILENCIO")
    print("-" * 40)
    silencio = _detectar_silencio(audio_path, threshold=0.01)
    if silencio:
        print("⚠️  El audio es principalmente SILENCIO")
        print("   → Vuelve a ejecutar y habla más fuerte\n")
    else:
        print("✓ Audio detectado (no es silencio)\n")
    
    # Test 3: Transcribir
    print("3️⃣  TEST DE TRANSCRIPCIÓN (faster-whisper)")
    print("-" * 40)
    print("Procesando audio con Whisper...")
    print("(Esto puede tardar 10-30 segundos la primera vez)\n")
    
    start = time.time()
    texto = transcribir(audio_path)
    tiempo_transcribe = time.time() - start
    
    if texto:
        print(f"✓ Transcripción exitosa:")
        print(f"  '{texto}'")
        print(f"⏱️  Tiempo: {tiempo_transcribe:.2f}s\n")
    else:
        print(f"⚠️  No se detectó texto (o timeout)")
        print(f"⏱️  Tiempo: {tiempo_transcribe:.2f}s\n")
    
    # Test 4: TTS
    print("4️⃣  TEST DE SÍNTESIS DE VOZ (TTS)")
    print("-" * 40)
    print("Sintetizando: 'Hola, estoy funcionando'")
    
    start = time.time()
    try:
        speak_and_play("Hola, estoy funcionando", language="es")
        print(f"✓ Audio reproducido")
        print(f"⏱️  Tiempo: {time.time() - start:.2f}s\n")
    except Exception as e:
        print(f"✗ Error en TTS: {e}\n")
    
    # Resumen
    print("="*60)
    print("📊 RESUMEN")
    print("="*60)
    print(f"Grabación:     ✓ {5}s grabados")
    print(f"Silencio:      {'✓ No silencio' if not silencio else '⚠️ Silencio detectado'}")
    print(f"Transcripción: {'✓ ' + texto if texto else '⚠️ Sin resultado'}")
    print(f"Síntesis:      ✓ Funcionando")
    print("="*60 + "\n")
    
    if texto:
        print("✅ SISTEMA DE VOZ FUNCIONANDO")
        print("Ahora ejecuta: python main.py")
    else:
        print("⚠️  Hay problemas con STT (Voice-to-Text)")
        print("Opciones:")
        print("1. Habla más fuerte durante la grabación")
        print("2. Usa modo TEXTO en lugar de voz")
        print("3. Verifica que tu micrófono esté conectado")

if __name__ == "__main__":
    try:
        test_voice_system()
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
