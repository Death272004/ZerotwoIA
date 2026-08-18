@echo off
setlocal
cd /d "%~dp0"

set "VENV_DIR=%~dp0.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

echo ========================================
echo ZeroTwoIA - compilar EXE
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

echo Instalando dependencias del proyecto...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 goto :error

"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Instalando PyInstaller...
"%PYTHON_EXE%" -m pip install pyinstaller
if errorlevel 1 goto :error

echo.
echo Compilando carpeta distribuible...
"%PYTHON_EXE%" -m PyInstaller --clean --noconfirm ZeroTwoIA.spec
if errorlevel 1 goto :error

echo.
echo Build terminado:
echo dist\ZeroTwoIA\ZeroTwoIA.exe
echo.
echo Para crear el acceso directo del escritorio con icono:
echo CREAR_ACCESO_DIRECTO.bat
echo.
echo Copia la carpeta completa dist\ZeroTwoIA para llevar la app a otro equipo.
echo El otro equipo tambien necesita Ollama instalado y el modelo configurado.
pause
exit /b 0

:error
echo.
echo ERROR: La compilacion fallo.
pause
exit /b 1
