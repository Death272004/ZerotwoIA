# ZeroTwoIA - Guía Rápida de Uso

## ⚡ Inicio Rápido

### Opción 1: App visual (Recomendado)

1. Ve a la carpeta del proyecto
2. **Doble clic en `INICIAR.bat`**
3. Se abre la ventana de ZeroTwoIA

La app visual incluye:

- Chat dedicado para escribir y leer respuestas.
- Botón de micrófono para hablarle.
- Botón para cambiar la voz y escuchar una prueba rápida.
- Respuesta por voz con `edge-tts`.
- Contador de tiempo de respuesta.
- Espectro animado para grabación, pensamiento y voz.

### Opción 0: Instalar todo en una PC nueva

Después de clonar el proyecto en Windows, ejecuta:

```bat
INSTALAR_TODO.bat
```

Ese script verifica Python y Ollama, intenta instalarlos con `winget` si faltan,
crea `.venv`, instala dependencias, descarga el modelo `llama3.2:1b`, compila el
`.exe` y crea el acceso directo del escritorio.

### Opción 2: Consola manual

**Terminal 1 - Ollama:**

```powershell
ollama serve
```

**Terminal 2 - ZeroTwo:**

```powershell
cd "ruta\a\ZeroTwoIA"
python main.py
```

También puedes usar el `.bat` en modo consola:

```powershell
set ZEROTWO_MODE=console
INICIAR.bat
```

### Opción 3: Ejecutable de Windows

Para generar una carpeta distribuible con `ZeroTwoIA.exe`:

```bat
COMPILAR_EXE.bat
```

El resultado queda en:

```text
dist\ZeroTwoIA\ZeroTwoIA.exe
```

Copia la carpeta completa `dist\ZeroTwoIA` si quieres mover la app a otro equipo.
El ejecutable incluye la interfaz visual y el icono de ZeroTwoIA, pero sigue
necesitando Ollama instalado en Windows para responder con el modelo local.

Para ejecutar el build desde el proyecto:

```bat
EJECUTAR_EXE.bat
```

---

## 🔧 Solución de problemas

### Error: "Ollama no responde"

**Solución:**

```powershell
# Terminal nueva - Verifica que mistral está descargado
ollama list

# Si no aparece "mistral", descárgalo:
ollama pull mistral

# Luego inicia Ollama
ollama serve
```

### Error: "Puerto 11434 ya en uso"

Significa Ollama **ya está corriendo**. Solo abre otra terminal para ZeroTwo.

### Error de audio

La voz se genera como MP3 con `edge-tts` y se reproduce con `pygame`.
Si no escuchas nada, revisa el volumen de Windows y ejecuta:

```powershell
pip install -r requirements.txt
```

---

## 🎙️ Modos de Uso

**Modo Texto:**

```
Tú: hola
ZeroTwo: [respuesta en texto]
```

**Modo Voz:**

```
Tú: [presiona Enter]
🎙 Escuchando (6 segundos)...
ZeroTwo: [respuesta en voz + texto]
```

**Modo Híbrido (Default):**

- Enter vacío = graba voz
- Escribir = usa texto
- Responde siempre en voz + texto

---

## 📋 Requisitos

✅ Python 3.11
✅ Ollama + modelo "llama3.2:1b"
✅ Dependencias Python del archivo `requirements.txt`

Instalación recomendada:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 Estado del Proyecto

| Componente             | Estado                   |
| ---------------------- | ------------------------ |
| STT (Voz → Texto)      | ✅ Funciona              |
| TTS (Texto → Voz)      | ✅ Funciona (edge-tts)   |
| Intención (regex+LLM)  | ✅ Funciona              |
| Ollama (Mistral)       | ⚠️ Requiere verificación |
| Personalidad Zero Two  | ✅ Funciona              |
| Base de datos (Memory) | ✅ Funciona              |

---

## 💾 Estructura

```
ZeroTwoIA/
├── main.py                  # Punto de entrada en consola
├── ui_app.py                # App visual de escritorio
├── config.py                # Configuración
├── INICIAR.bat              # Script de inicio
├── core/
│   ├── core_brain.py        # Ollama + LLM
│   ├── intent.py            # Detección de intención
│   ├── memory.py            # Base de datos
│   └── personality.py       # Prompt de Zero Two
├── agents/
│   ├── code_agent.py        # Agente de programación
│   ├── system_agent.py      # Agente de sistema
│   └── web_agent.py         # Agente web
├── tools/
│   ├── app_launcher.py      # Abrir aplicaciones
│   └── browser.py           # Búsqueda web
└── voice/
    ├── stt.py               # Speech-to-Text (Whisper)
    ├── tts.py               # Text-to-Speech (edge-tts)
    └── data/
        └── zerotwo_voice.wav # Referencia de voz
```

---

**Próximos pasos:**

1. Verifica que `ollama list` muestre "llama3.2:1b"
2. Inicia con `INICIAR.bat` o manualmente
3. Escribe "Hola" y disfruta 🎉
