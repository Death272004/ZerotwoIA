@echo off
setlocal
cd /d "%~dp0"

set "VENV_DIR=%~dp0.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
if "%ZEROTWO_MODEL%"=="" set "ZEROTWO_MODEL=llama3.2:1b"
set "MODEL_NAME=%ZEROTWO_MODEL%"

echo ========================================
echo ZeroTwoIA - inicio automatico
echo ========================================
echo.

if not exist "%PYTHON_EXE%" (
    echo Creando entorno virtual en .venv...
    where python >nul 2>&1
    if not errorlevel 1 (
        python -m venv "%VENV_DIR%"
    ) else (
        where py >nul 2>&1
        if not errorlevel 1 (
            py -3 -m venv "%VENV_DIR%"
        ) else (
            echo ERROR: No encontre Python.
            echo Instala Python 3.10+ desde https://www.python.org/downloads/
            echo Marca la opcion "Add python.exe to PATH" durante la instalacion.
            pause
            exit /b 1
        )
    )
)

if not exist "%PYTHON_EXE%" (
    echo ERROR: No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

echo Instalando/actualizando dependencias...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: No se pudo actualizar pip.
    pause
    exit /b 1
)

"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
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

ollama list >nul 2>&1
if errorlevel 1 (
    echo Iniciando Ollama...
    start "Ollama Server" cmd /k "ollama serve"
    timeout /t 5 /nobreak >nul
)

ollama list | findstr /I /C:"%MODEL_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Descargando modelo %MODEL_NAME%...
    ollama pull %MODEL_NAME%
    if errorlevel 1 (
        echo ERROR: No se pudo descargar el modelo %MODEL_NAME%.
        pause
        exit /b 1
    )
)

echo.
echo Iniciando ZeroTwoIA...
echo.
"%PYTHON_EXE%" main.py

echo.
echo ZeroTwoIA se cerro.
pause
