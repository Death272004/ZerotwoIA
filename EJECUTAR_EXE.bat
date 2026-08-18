@echo off
setlocal
cd /d "%~dp0"

set "APP_EXE=%~dp0dist\ZeroTwoIA\ZeroTwoIA.exe"
if not exist "%APP_EXE%" (
    echo No encontre "%APP_EXE%".
    echo Ejecuta primero COMPILAR_EXE.bat.
    pause
    exit /b 1
)

where ollama >nul 2>&1
if errorlevel 1 (
    echo ERROR: No encontre Ollama.
    echo Instala Ollama desde https://ollama.com/download
    pause
    exit /b 1
)

if "%ZEROTWO_MODEL%"=="" set "ZEROTWO_MODEL=llama3.2:1b"

ollama list >nul 2>&1
if errorlevel 1 (
    echo Iniciando Ollama...
    start "Ollama Server" cmd /k "ollama serve"
    timeout /t 5 /nobreak >nul
)

ollama list | findstr /I /C:"%ZEROTWO_MODEL%" >nul 2>&1
if errorlevel 1 (
    echo Descargando modelo %ZEROTWO_MODEL%...
    ollama pull %ZEROTWO_MODEL%
    if errorlevel 1 (
        echo ERROR: No se pudo descargar el modelo %ZEROTWO_MODEL%.
        pause
        exit /b 1
    )
)

start "ZeroTwoIA" "%APP_EXE%"
