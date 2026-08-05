# ZeroTwoIA - Guía Rápida de Uso

## ⚡ Inicio Rápido

### Opción 1: Doble clic (Recomendado)

1. Ve a la carpeta del proyecto
2. **Doble clic en `INICIAR.bat`**
3. Se abren 2 ventanas automáticamente

### Opción 2: Terminal manual

**Terminal 1 - Ollama:**

```powershell
ollama serve
```

**Terminal 2 - ZeroTwo:**

```powershell
cd "c:\Users\rrpin\Documents\Proyectos personales\Proyectos personales\ZeroIACLaude - copia\ZeroTwoIA"
python main.py
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

### Error de audio (wav inválido)

Se corrigió automáticamente. Ahora usa `winsound` nativo.

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
✅ Ollama + modelo "mistral"
✅ Dependencias: edge-tts, ollama, faster-whisper, sounddevice, soundfile

Todos ya instalados en el venv.

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
├── main.py                  # Punto de entrada
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

1. Verifica que `ollama list` muestre "mistral"
2. Inicia con `INICIAR.bat` o manualmente
3. Escribe "Hola" y disfruta 🎉
