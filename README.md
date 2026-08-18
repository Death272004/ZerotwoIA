# ZeroTwoIA

Asistente local de escritorio inspirado en Zero Two, con interfaz visual, chat,
voz, memoria, comandos para abrir aplicaciones de Windows y modelo local con
Ollama.

El objetivo del proyecto es tener una asistente tipo copiloto/Jarvis, pero con
tematica Zero Two: rapida, directa, expresiva y con respuestas por texto y voz.

## Funciones actuales

- Interfaz visual propia con chat dedicado.
- Respuesta por texto y voz.
- Boton de microfono para hablarle.
- Boton para cambiar la voz desde la interfaz.
- Presentacion por voz al iniciar.
- Espectro circular tipo HUD que reacciona a microfono, pensamiento y voz.
- Contador de tiempo de respuesta.
- Memoria local con SQLite.
- Comandos para abrir aplicaciones de Windows.
- Build de Windows con `ZeroTwoIA.exe` + dependencias.
- Script de instalacion completa para PC nueva.

## Requisitos

Para una instalacion normal en Windows necesitas:

- Windows 10/11.
- Git.
- Python 3.10 o 3.11.
- Ollama.
- Internet la primera vez para instalar dependencias y descargar el modelo.
- Microfono y salida de audio si quieres usar voz.

El modelo por defecto es:

```text
llama3.2:1b
```

Se usa por velocidad. Puedes cambiarlo por otro modelo de Ollama si prefieres
mas calidad.

## Instalacion en una PC nueva

Despues de clonar el repositorio:

```powershell
git clone https://github.com/Death272004/ZerotwoIA.git
cd ZerotwoIA
.\INSTALAR_TODO.bat
```

`INSTALAR_TODO.bat` intenta preparar todo el entorno:

- Verifica Python.
- Intenta instalar Python con `winget` si falta.
- Crea `.venv`.
- Instala dependencias de `requirements.txt`.
- Verifica Ollama.
- Intenta instalar Ollama con `winget` si falta.
- Inicia Ollama si no esta respondiendo.
- Descarga `llama3.2:1b` si no esta instalado.
- Compila el `.exe`.
- Crea un acceso directo en el escritorio.

Si algo falla, el script deja la ventana abierta y muestra que punto debes
corregir.

## Uso normal

Desde la carpeta del proyecto:

```powershell
.\INICIAR.bat
```

Esto abre la app visual por defecto.

Para usar el modo consola:

```powershell
set ZEROTWO_MODE=console
.\INICIAR.bat
```

## Compilar el ejecutable

Para generar el ejecutable distribuible:

```powershell
.\COMPILAR_EXE.bat
```

El resultado queda en:

```text
dist\ZeroTwoIA\ZeroTwoIA.exe
```

Importante: esta version es `.exe + dependencias`. Si quieres mover la app a
otro equipo, copia la carpeta completa:

```text
dist\ZeroTwoIA
```

El otro equipo tambien necesita Ollama instalado y el modelo descargado.

Para ejecutar el build ya compilado:

```powershell
.\EJECUTAR_EXE.bat
```

## Acceso directo con icono

Despues de compilar, puedes crear el acceso directo del escritorio:

```powershell
.\CREAR_ACCESO_DIRECTO.bat
```

El acceso directo apunta a:

```text
dist\ZeroTwoIA\ZeroTwoIA.exe
```

Si Windows muestra un icono viejo, elimina el acceso directo anterior y ejecuta
`CREAR_ACCESO_DIRECTO.bat` otra vez.

## Cambiar modelo de Ollama

Modelo rapido recomendado:

```powershell
set ZEROTWO_MODEL=llama3.2:1b
.\INICIAR.bat
```

Modelo con mas calidad, pero mas lento:

```powershell
set ZEROTWO_MODEL=mistral
.\INICIAR.bat
```

Tambien puedes probar otros modelos instalados en Ollama:

```powershell
set ZEROTWO_MODEL=llama3.1:8b
.\INICIAR.bat
```

Mientras mas grande sea el modelo, mas tardara en responder.

## Cambiar voz

La interfaz incluye el boton `Cambiar voz`. Al presionarlo:

- Cambia entre voces disponibles.
- Guarda la voz elegida en `data/voice_config.json`.
- Reproduce una frase corta de prueba.
- Usa esa voz en las siguientes respuestas.

Tambien puedes configurar la voz desde PowerShell:

```powershell
set ZEROTWO_VOICE=es-MX-DaliaNeural
set ZEROTWO_VOICE_RATE=+8%
set ZEROTWO_VOICE_PITCH=+12Hz
.\INICIAR.bat
```

Nota: el proyecto no clona voces de actrices reales. Usa voces neurales de
`edge-tts` configuradas para acercarse al estilo deseado.

## Comandos para abrir aplicaciones

Puedes escribir comandos como:

```text
abre word
abre excel
abre powerpoint
abre chrome
abre calculadora
abre paint
abre spotify
abre discord
abre steam
abre explorer
abre powershell
```

Las rutas principales se configuran en `config.py`, en la variable `APPS`.
Si una app no abre en tu PC, revisa si esta instalada o ajusta su ruta.

## Solucion de problemas

### Ollama no esta instalado

Instalalo desde:

```text
https://ollama.com/download
```

Luego abre una terminal y verifica:

```powershell
ollama --version
ollama list
```

### Ollama no responde

Inicia el servidor:

```powershell
ollama serve
```

En otra terminal, verifica el modelo:

```powershell
ollama list
ollama pull llama3.2:1b
```

### El modelo responde muy lento

Usa el modelo rapido:

```powershell
set ZEROTWO_MODEL=llama3.2:1b
.\INICIAR.bat
```

Tambien ayuda cerrar programas pesados y evitar modelos grandes si no tienes
GPU suficiente.

### No se escucha la voz

Revisa:

- Volumen de Windows.
- Dispositivo de salida correcto.
- Que `pygame` este instalado desde `requirements.txt`.
- Que tengas internet para que `edge-tts` genere la voz.

Puedes reinstalar dependencias con:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### El microfono se queda grabando o no escucha

Revisa permisos de microfono en Windows y prueba cerrar otras apps que esten
usando el microfono. La app debe grabar una sola toma por activacion.

### Word no abre

Verifica que Microsoft Office este instalado. Si el comando automatico no lo
encuentra, edita `config.py` y cambia la ruta de `word` dentro de `APPS`.

Ejemplo:

```python
APPS = {
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
}
```

## Estructura del proyecto

```text
ZeroTwoIA/
├── main.py                    # Entrada modo consola
├── ui_app.py                  # Interfaz visual
├── config.py                  # Modelo, voz, rutas y opciones
├── requirements.txt           # Dependencias Python
├── INICIAR.bat                # Inicio normal
├── INSTALAR_TODO.bat          # Instalacion completa para PC nueva
├── COMPILAR_EXE.bat           # Build con PyInstaller
├── EJECUTAR_EXE.bat           # Ejecuta el build compilado
├── CREAR_ACCESO_DIRECTO.bat   # Acceso directo con icono
├── DIAGNOSTICO.bat            # Diagnostico del entorno
├── ZeroTwoIA.spec             # Configuracion de PyInstaller
├── assets/
│   ├── zerotwo_icon.ico
│   └── zerotwo_icon.png
├── core/
│   ├── core_brain.py          # Conexion con Ollama
│   ├── intent.py              # Deteccion de intencion
│   ├── memory.py              # Memoria SQLite
│   └── personality.py         # Prompt/persona de ZeroTwo
├── agents/
│   ├── code_agent.py          # Ayuda de programacion
│   ├── system_agent.py        # Acciones del sistema
│   └── web_agent.py           # Busqueda web / URLs
├── tools/
│   ├── app_launcher.py        # Apertura de aplicaciones
│   └── browser.py             # Utilidades web
├── voice/
│   ├── stt.py                 # Voz a texto
│   └── tts.py                 # Texto a voz
└── data/
    └── memory.db              # Memoria local generada
```

## Estado actual

| Componente | Estado |
| --- | --- |
| App visual | Funcional |
| Chat de texto | Funcional |
| Voz TTS | Funcional con `edge-tts` + `pygame` |
| Microfono STT | Funcional con Whisper |
| Memoria local | Funcional con SQLite |
| Comandos de Windows | Funcionales, dependen de rutas/apps instaladas |
| Build `.exe` | Preparado con PyInstaller |
| Instalacion completa | Preparada con `INSTALAR_TODO.bat` |

## Flujo recomendado de desarrollo

```powershell
git pull origin main
.\INICIAR.bat
```

Para probar build:

```powershell
.\COMPILAR_EXE.bat
.\EJECUTAR_EXE.bat
```

Para preparar una PC limpia:

```powershell
.\INSTALAR_TODO.bat
```
