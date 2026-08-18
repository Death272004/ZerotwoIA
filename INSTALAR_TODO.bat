@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "APP_NAME=ZeroTwoIA"
if "%ZEROTWO_MODEL%"=="" set "ZEROTWO_MODEL=llama3.2:1b"
set "MODEL_NAME=%ZEROTWO_MODEL%"
set "VENV_DIR=%~dp0.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "APP_EXE=%~dp0dist\ZeroTwoIA\ZeroTwoIA.exe"

echo ========================================
echo %APP_NAME% - instalacion completa
echo ========================================
echo.
echo Este script prepara una PC nueva para ejecutar y compilar ZeroTwoIA.
echo Requiere internet la primera vez.
echo.

call :ensure_python
if errorlevel 1 goto :error

call :ensure_venv
if errorlevel 1 goto :error

call :install_python_deps
if errorlevel 1 goto :error

call :ensure_ollama
if errorlevel 1 goto :error

call :ensure_model
if errorlevel 1 goto :error

call :build_exe
if errorlevel 1 goto :error

call :create_shortcut

echo.
echo ========================================
echo Instalacion terminada correctamente.
echo ========================================
echo.
echo Ejecutable:
echo %APP_EXE%
echo.
echo Tambien puedes iniciar con:
echo INICIAR.bat
echo.
pause
exit /b 0

:ensure_python
echo [1/6] Verificando Python...
where python >nul 2>&1
if not errorlevel 1 (
    python --version
    exit /b 0
)

where py >nul 2>&1
if not errorlevel 1 (
    py -3 --version
    exit /b 0
)

echo Python no esta instalado o no esta en PATH.
call :try_winget "Python.Python.3.11" "Python 3.11"
if errorlevel 1 (
    echo.
    echo ERROR: Instala Python 3.10 o 3.11 desde:
    echo https://www.python.org/downloads/
    echo.
    echo Marca "Add python.exe to PATH" durante la instalacion.
    exit /b 1
)

where python >nul 2>&1
if not errorlevel 1 exit /b 0
where py >nul 2>&1
if not errorlevel 1 exit /b 0

echo ERROR: Python se instalo, pero no aparece en PATH. Cierra esta ventana y ejecuta otra vez.
exit /b 1

:ensure_venv
echo.
echo [2/6] Preparando entorno virtual...
if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" --version
    exit /b 0
)

where python >nul 2>&1
if not errorlevel 1 (
    python -m venv "%VENV_DIR%"
) else (
    py -3 -m venv "%VENV_DIR%"
)

if not exist "%PYTHON_EXE%" (
    echo ERROR: No se pudo crear .venv.
    exit /b 1
)

"%PYTHON_EXE%" --version
exit /b 0

:install_python_deps
echo.
echo [3/6] Instalando dependencias Python...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

"%PYTHON_EXE%" -m pip install pyinstaller
if errorlevel 1 exit /b 1

exit /b 0

:ensure_ollama
echo.
echo [4/6] Verificando Ollama...
where ollama >nul 2>&1
if not errorlevel 1 (
    ollama --version
    exit /b 0
)

echo Ollama no esta instalado o no esta en PATH.
call :try_winget "Ollama.Ollama" "Ollama"
if errorlevel 1 (
    echo.
    echo ERROR: Instala Ollama desde:
    echo https://ollama.com/download
    exit /b 1
)

where ollama >nul 2>&1
if not errorlevel 1 exit /b 0

echo ERROR: Ollama se instalo, pero no aparece en PATH. Cierra esta ventana y ejecuta otra vez.
exit /b 1

:ensure_model
echo.
echo [5/6] Verificando servicio y modelo de Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo Iniciando Ollama...
    start "Ollama Server" cmd /k "ollama serve"
    timeout /t 8 /nobreak >nul
)

ollama list >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama no responde. Abre Ollama manualmente y ejecuta este script otra vez.
    exit /b 1
)

ollama list | findstr /I /C:"%MODEL_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo Modelo listo: %MODEL_NAME%
    exit /b 0
)

echo Descargando modelo %MODEL_NAME%...
ollama pull %MODEL_NAME%
if errorlevel 1 (
    echo ERROR: No se pudo descargar el modelo %MODEL_NAME%.
    exit /b 1
)

exit /b 0

:build_exe
echo.
echo [6/6] Compilando ejecutable...
"%PYTHON_EXE%" -m PyInstaller --clean --noconfirm ZeroTwoIA.spec
if errorlevel 1 (
    echo ERROR: La compilacion fallo.
    exit /b 1
)

if not exist "%APP_EXE%" (
    echo ERROR: PyInstaller termino, pero no encontre:
    echo %APP_EXE%
    exit /b 1
)

echo Build listo: %APP_EXE%
exit /b 0

:create_shortcut
if exist "CREAR_ACCESO_DIRECTO.bat" (
    echo.
    echo Creando acceso directo en el escritorio...
    call "CREAR_ACCESO_DIRECTO.bat" /silent
)
exit /b 0

:try_winget
set "PACKAGE_ID=%~1"
set "PACKAGE_NAME=%~2"

where winget >nul 2>&1
if errorlevel 1 (
    echo No encontre winget para instalar %PACKAGE_NAME% automaticamente.
    exit /b 1
)

echo Intentando instalar %PACKAGE_NAME% con winget...
winget install --id "%PACKAGE_ID%" --exact --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo winget no pudo instalar %PACKAGE_NAME%.
    exit /b 1
)

exit /b 0

:error
echo.
echo ========================================
echo La instalacion no pudo completarse.
echo ========================================
echo Revisa el mensaje anterior, corrige ese punto y ejecuta INSTALAR_TODO.bat otra vez.
echo.
pause
exit /b 1
