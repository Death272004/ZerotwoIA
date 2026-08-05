#!/usr/bin/env python3
"""
test_latencia.py - Compara latencia antes/después de optimizaciones
Uso: python test_latencia.py
"""

import time
import sys

def test_streaming_latency():
    """Prueba latencia de streaming vs no-streaming."""
    from core.core_brain import enviar_mensaje, enviar_mensaje_streaming
    
    test_query = "¿Cuál es la capital de España? (responde en una línea)"
    
    print("\n" + "="*60)
    print("⏱️  TEST DE LATENCIA - ZeroTwo")
    print("="*60)
    
    # Test 1: Sin streaming (viejo)
    print("\n1️⃣  ANTES (sin streaming):")
    print("-" * 40)
    start = time.time()
    texto1, _ = enviar_mensaje(test_query)
    time_without = time.time() - start
    print(f"   Respuesta: {texto1[:60]}...")
    print(f"   ⏱️  Tiempo total: {time_without:.2f}s")
    
    # Test 2: Con streaming (nuevo)
    print("\n2️⃣  DESPUÉS (con streaming):")
    print("-" * 40)
    chunks_recibidos = 0
    primer_chunk_time = None
    
    def on_chunk(chunk):
        nonlocal chunks_recibidos, primer_chunk_time
        chunks_recibidos += 1
        if primer_chunk_time is None:
            primer_chunk_time = time.time() - start_stream
        sys.stdout.write(chunk)
        sys.stdout.flush()
    
    start_stream = time.time()
    texto2, _ = enviar_mensaje_streaming(test_query, callback=on_chunk)
    time_with = time.time() - start_stream
    print(f"\n\n   ⏱️  Primer chunk en: {primer_chunk_time:.2f}s")
    print(f"   ⏱️  Tiempo total: {time_with:.2f}s")
    print(f"   📦 Chunks recibidos: {chunks_recibidos}")
    
    # Comparativa
    print("\n" + "="*60)
    print("📊 COMPARATIVA:")
    print("="*60)
    mejora = ((time_without - time_with) / time_without) * 100
    print(f"  Sin streaming:    {time_without:.2f}s")
    print(f"  Con streaming:    {time_with:.2f}s")
    print(f"  Primer chunk:     {primer_chunk_time:.2f}s")
    print(f"  ✨ Mejora:        {mejora:.1f}% más rápido")
    print(f"  👁️  Usuario ve:    Respuesta en {primer_chunk_time:.2f}s (vs esperar {time_without:.2f}s)")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_streaming_latency()
        print("✅ Test completado exitosamente")
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
