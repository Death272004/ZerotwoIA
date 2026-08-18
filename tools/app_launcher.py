# tools/app_launcher.py

import os
import shutil
import subprocess
from pathlib import Path

from config import APPS

try:
    import winreg
except ImportError:
    winreg = None


ALIASES = {
    "bloc de notas": "notepad",
    "visual studio": "vscode",
    "visual studio code": "vscode",
    "power point": "powerpoint",
    "calc": "calculadora",
}

DISPLAY_NAMES = {
    "chrome": "Chrome",
    "firefox": "Firefox",
    "notepad": "Bloc de notas",
    "vscode": "Visual Studio Code",
    "word": "Word",
    "excel": "Excel",
    "powerpoint": "PowerPoint",
    "calculadora": "Calculadora",
}

OFFICE_EXES = {
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
}

WINDOWS_PROTOCOLS = {
    "word": "ms-word:",
    "excel": "ms-excel:",
    "powerpoint": "ms-powerpoint:",
    "calculadora": "calculator:",
}


def _canonical_name(name: str) -> str:
    clean = " ".join(name.strip().lower().split())
    return ALIASES.get(clean, clean)


def _configured_command(name: str) -> list[str]:
    command = APPS.get(name)
    if not command:
        return []
    if isinstance(command, (list, tuple)):
        return [str(part) for part in command if str(part).strip()]
    return [str(command)]


def _registry_app_path(exe_name: str) -> str:
    if winreg is None:
        return ""

    key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}"
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(root, key_path) as key:
                value, _ = winreg.QueryValueEx(key, None)
                if value:
                    return str(value)
        except OSError:
            continue
    return ""


def _office_paths(app: str) -> list[str]:
    exe_name = OFFICE_EXES.get(app)
    if not exe_name:
        return []

    roots = [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
    ]
    office_dirs = [
        r"Microsoft Office\root\Office16",
        r"Microsoft Office\Office16",
        r"Microsoft Office\Office15",
        r"Microsoft Office\Office14",
    ]

    paths = []
    for root in roots:
        if not root:
            continue
        for office_dir in office_dirs:
            paths.append(str(Path(root) / office_dir / exe_name))
    return paths


def _candidate_commands(name: str) -> list[list[str]]:
    commands = []
    configured = _configured_command(name)
    if configured:
        commands.append(configured)

    exe_name = OFFICE_EXES.get(name)
    if exe_name:
        registry_path = _registry_app_path(exe_name)
        if registry_path:
            commands.append([registry_path])

        for path in _office_paths(name):
            commands.append([path])

        commands.append([exe_name])
        commands.append([exe_name.lower()])

    if name == "calculadora":
        commands.extend([["calc.exe"], ["calc"]])

    if name == "notepad":
        commands.extend([["notepad.exe"], ["notepad"]])

    return commands


def _exists_or_is_on_path(command: list[str]) -> bool:
    if not command:
        return False
    executable = command[0]
    if Path(executable).exists():
        return True
    return shutil.which(executable) is not None


def _try_startfile(target: str) -> bool:
    if os.name != "nt" or not hasattr(os, "startfile"):
        return False
    try:
        os.startfile(target)
        return True
    except OSError:
        return False


def _try_cmd_start(target: str) -> bool:
    if os.name != "nt":
        return False
    try:
        subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)
        return True
    except OSError:
        return False


def open_app(name: str) -> str:
    app = _canonical_name(name)
    display = DISPLAY_NAMES.get(app, app)

    if app not in APPS and app not in OFFICE_EXES and app not in WINDOWS_PROTOCOLS:
        return f"No tengo registrada la aplicacion '{name}'."

    errors = []
    for command in _candidate_commands(app):
        try:
            if not _exists_or_is_on_path(command):
                continue
            subprocess.Popen(command)
            return f"Abriendo {display}, Darling."
        except OSError as exc:
            errors.append(str(exc))

    protocol = WINDOWS_PROTOCOLS.get(app)
    if protocol and _try_startfile(protocol):
        return f"Abriendo {display}, Darling."

    if app in OFFICE_EXES and _try_cmd_start(OFFICE_EXES[app]):
        return f"Intentando abrir {display}, Darling."

    hint = ""
    if app in OFFICE_EXES:
        hint = " Revisa que Microsoft Office este instalado o agrega la ruta exacta en config.py."
    elif errors:
        hint = f" Ultimo error: {errors[-1]}"
    return f"No pude abrir {display}.{hint}"
