# agents/system_agent.py

from tools.app_launcher import open_app

ALLOWED_ACTIONS = {"open_app"}


def execute_command(command: dict) -> str:
    """
    command esperado:
    {
        "action": "open_app",
        "target": "chrome"   # nombre de la app
    }
    """
    action = command.get("action")

    if action not in ALLOWED_ACTIONS:
        return f"Acción '{action}' no permitida."

    if action == "open_app":
        target = command.get("target", "").strip()
        if not target:
            return "No especificaste qué aplicación abrir."
        return open_app(target)

    return "Comando no reconocido."
