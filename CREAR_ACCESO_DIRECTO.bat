@echo off
setlocal
cd /d "%~dp0"

set "APP_EXE=%~dp0dist\ZeroTwoIA\ZeroTwoIA.exe"
set "APP_ICON=%~dp0assets\zerotwo_icon.ico"
set "SHORTCUT_NAME=ZeroTwoIA.lnk"

if not exist "%APP_EXE%" (
    echo No encontre "%APP_EXE%".
    echo Ejecuta primero COMPILAR_EXE.bat para generar el ejecutable.
    pause
    exit /b 1
)

if not exist "%APP_ICON%" (
    echo No encontre "%APP_ICON%".
    echo El acceso directo se creara, pero Windows usara el icono del ejecutable.
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$desktop = [Environment]::GetFolderPath('Desktop');" ^
  "$shortcutPath = Join-Path $desktop '%SHORTCUT_NAME%';" ^
  "$shell = New-Object -ComObject WScript.Shell;" ^
  "$shortcut = $shell.CreateShortcut($shortcutPath);" ^
  "$shortcut.TargetPath = '%APP_EXE%';" ^
  "$shortcut.WorkingDirectory = '%~dp0dist\ZeroTwoIA';" ^
  "$shortcut.Description = 'ZeroTwoIA';" ^
  "if (Test-Path '%APP_ICON%') { $shortcut.IconLocation = '%APP_ICON%' } else { $shortcut.IconLocation = '%APP_EXE%' };" ^
  "$shortcut.Save();" ^
  "Write-Host 'Acceso directo creado en:' $shortcutPath"

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo crear el acceso directo.
    pause
    exit /b 1
)

echo.
echo Listo. Si Windows sigue mostrando un icono viejo, elimina el acceso directo anterior
echo del escritorio y ejecuta este archivo otra vez.
pause
