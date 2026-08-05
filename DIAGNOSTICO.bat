@echo off
REM Verificar estado de Ollama

echo.
echo ===== DIAGNÓSTICO OLLAMA =====
echo.

echo [1] Verificando si Ollama está corriendo...
curl -s http://127.0.0.1:11434/api/tags > nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Ollama está corriendo en 127.0.0.1:11434
) else (
    echo ✗ Ollama NO está corriendo
    echo   Inicia con: ollama serve
    pause
    exit /b 1
)

echo.
echo [2] Verificando modelos disponibles...
ollama list

echo.
echo [3] Verificando si "mistral" está descargado...
ollama list | find "mistral" > nul
if %errorlevel% == 0 (
    echo ✓ Mistral está descargado
) else (
    echo ✗ Mistral NO está descargado
    echo   Descargando... (puede tomar 5-10 minutos)
    ollama pull mistral
)

echo.
echo [4] Probando conexión a Mistral...
python -c "import ollama; resp = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': 'hola'}]); print('✓ Ollama responde:', resp['message']['content'][:50])"

if %errorlevel% == 0 (
    echo.
    echo ✓✓✓ TODO OK - Ollama está listo para ZeroTwo
    echo.
    pause
) else (
    echo.
    echo ✗✗✗ Error al conectar con Ollama
    echo   Reinicia: ollama serve
    echo.
    pause
    exit /b 1
)
