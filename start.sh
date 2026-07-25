#!/bin/bash

# start.sh - Script de inicialización y despliegue rápido para SecureLock AI
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo "          INICIANDO PIPELINE DE SECURELOCK AI 🛡️           "
echo "=========================================================="
echo ""

# Validar y crear entorno virtual venv si no existe
if [ ! -d "venv" ]; then
    echo "[!] Entorno virtual 'venv' no detectado. Creándolo e instalando dependencias..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "[x] Entorno virtual 'venv' detectado. Activándolo..."
    source venv/bin/activate
fi

echo ""
echo "[*] Servidor FastAPI arrancando de forma local en http://127.0.0.1:8000"
echo "[*] Abre tu navegador web en esa dirección para interactuar con la interfaz."
echo "[!] Nota de Primera Inferencia: La primera vez que registres o verifiques un rostro,"
echo "    DeepFace descargará automáticamente los pesos del modelo VGG-Face y OpenCV (~20MB)."
echo "    Esto se realiza una sola vez de forma interna y automática."
echo ""
echo "Presiona Ctrl+C para detener el servidor de forma segura."
echo "----------------------------------------------------------"

# Iniciar servidor local usando explícitamente el binario de uvicorn del entorno virtual activo
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
