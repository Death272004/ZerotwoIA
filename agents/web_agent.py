# agents/web_agent.py

from tools.browser import search, open_url, open_youtube

_PREFIXES = (
    "busca ", "buscar ", "googlea ", "googlear ",
    "busca en internet ", "busca en la web ",
    "qué es ", "quién es ", "cómo se hace ",
    "información sobre ", "busca en youtube ",
    "pon en youtube ", "abre ",
)


def _clean_query(text: str) -> str:
    lower = text.lower()
    for prefix in _PREFIXES:
        if lower.startswith(prefix):
            return text[len(prefix):].strip()
    return text.strip()


def handle(intent: dict) -> str:
    raw = intent.get("query") or intent.get("raw", "")
    if not raw:
        return "No entendí qué buscar."

    lower = raw.lower()

    # Abre URL directa
    if any(lower.startswith(p) for p in ("abre http", "abre www")):
        return open_url(_clean_query(raw))

    # YouTube
    if "youtube" in lower:
        return open_youtube(_clean_query(raw))

    # Búsqueda general
    return search(_clean_query(raw))
