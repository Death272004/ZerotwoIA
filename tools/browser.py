# tools/browser.py

import webbrowser
import urllib.parse


def open_url(url: str) -> str:
    """Abre una URL directamente en el navegador por defecto."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Abriendo {url}"


def search(query: str) -> str:
    """Busca una query en Google y la abre en el navegador."""
    if not query.strip():
        return "No especificaste qué buscar."
    encoded = urllib.parse.quote_plus(query.strip())
    url = f"https://www.google.com/search?q={encoded}"
    webbrowser.open(url)
    return f'Buscando "{query.strip()}" en el navegador.'


def open_youtube(query: str) -> str:
    """Busca en YouTube."""
    encoded = urllib.parse.quote_plus(query.strip())
    url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(url)
    return f'Buscando "{query.strip()}" en YouTube.'
