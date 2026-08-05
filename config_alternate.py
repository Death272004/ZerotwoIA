# config_alternate.py - Modelos alternativos de Ollama
# 
# INSTRUCCIÓN: Copia la línea del modelo que quieras a config.py
# 
# Por ejemplo:
# Copia:      MODEL_NAME = "neural-chat:latest"
# Y reemplaza en config.py la línea actual de MODEL_NAME

# ⚡ ULTRA RÁPIDO (~0.5-1 seg por respuesta)
# MODEL_NAME = "tinyllama:latest"
# MODEL_OPTIONS = {"temperature": 0.7, "num_predict": 256}

# ⚡ RÁPIDO + BUENA CALIDAD (~1-1.5 seg) - RECOMENDADO
# MODEL_NAME = "neural-chat:latest"
# MODEL_OPTIONS = {"temperature": 0.8, "num_predict": 512}

# ⚡ RÁPIDO + MÁS CAPACIDADES (~1-2 seg)
# MODEL_NAME = "orca-2:latest"
# MODEL_OPTIONS = {"temperature": 0.8, "num_predict": 512}

# ⚠️ MODERADO (~1.5-2 seg) - Más preciso
# MODEL_NAME = "mistral:latest"
# MODEL_OPTIONS = {"temperature": 0.7, "num_predict": 1024}

# 🟨 LENTO PERO MUY INTELIGENTE (~2-3 seg)
# MODEL_NAME = "mistral:latest"  
# MODEL_OPTIONS = {"temperature": 0.7, "num_predict": 1024}

# 🔴 MUY LENTO + MÁS INTELIGENTE (~3-5 seg)
# MODEL_NAME = "mixtral:latest"
# MODEL_OPTIONS = {"temperature": 0.7, "num_predict": 1024}

# INSTALACIÓN DE MODELOS RÁPIDOS:
# En PowerShell:
#   ollama pull neural-chat:latest
#   ollama pull orca-2:latest  
#   ollama pull tinyllama:latest

# VERIFICAR MODELOS DESCARGADOS:
#   ollama list

# ---

# RECOMENDACIÓN PARA CHAT RÁPIDO COMO CLAUDE/CHATGPT:
# 1. Instala: ollama pull neural-chat:latest
# 2. En config.py, cambia a: MODEL_NAME = "neural-chat:latest"
# 3. Listo, responde ~50% más rápido

# PARA RESPUESTAS INSTANTÁNEAS (sacrificando calidad):
# 1. Instala: ollama pull tinyllama:latest
# 2. En config.py, cambia a: MODEL_NAME = "tinyllama:latest"
# 3. Respuestas en <1 segundo

# ---
# Notas:
# - Los cambios de modelo son instantáneos (sin reiniciar Ollama)
# - Prueba con cada modelo escribiendo: "Hola, ¿cómo estás?"
# - TIME BENCHMARK: Compara tiempo de respuesta entre modelos
