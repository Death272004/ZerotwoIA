@echo off
REM ZeroTwoIA - Iniciar todo en 2 ventanas

echo Iniciando Ollama...
start "Ollama Server" cmd /k "ollama serve"

echo Esperando 3 segundos...
timeout /t 3

echo.
echo Iniciando ZeroTwo...
start "ZeroTwo" cmd /k "cd /d ""%~dp0"" && python main.py"

echo.
echo ✓ Ollama y ZeroTwo iniciados
echo ✓ Cierra estas ventanas cuando termines
