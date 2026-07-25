import os
import base64
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Intentar importar DeepFace para resiliencia durante la fase de instalación
try:
    from deepface import DeepFace
except ImportError:
    DeepFace = None

app = FastAPI(
    title="SecureLock API - Sistema de Autenticación Biométrica Facial",
    description="Backend para inicio de sesión seguro mediante verificación de rostros usando DeepFace."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
REGISTERED_DIR = os.path.join(DATA_DIR, "users")

# Asegurar la existencia de las carpetas de datos
os.makedirs(REGISTERED_DIR, exist_ok=True)

if os.path.exists(TEMPLATES_DIR):
    app.mount("/static", StaticFiles(directory=TEMPLATES_DIR), name="static")

class AuthRequest(BaseModel):
    image: str  # String en formato DataURL o Base64 simple

def save_base64_image(base64_str: str, file_path: str):
    """Decodifica un string base64 y lo guarda en disco."""
    try:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        img_data = base64.b64decode(base64_str)
        with open(file_path, "wb") as f:
            f.write(img_data)
        return True
    except Exception as e:
        print(f"Error al decodificar imagen Base64: {e}")
        return False

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Sirve la interfaz web del sistema de autenticación."""
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(
        content="<h1>SecureLock Frontend no encontrado</h1><p>Asegúrate de que templates/index.html exista.</p>",
        status_code=404
    )

@app.post("/api/register")
async def register_user(payload: AuthRequest):
    """Registra el rostro maestro del usuario del sistema."""
    # Guardamos el rostro autorizado de forma fija como 'user_master.jpg'
    master_path = os.path.join(REGISTERED_DIR, "user_master.jpg")
    
    if not save_base64_image(payload.image, master_path):
        raise HTTPException(status_code=400, detail="Error al decodificar la imagen de registro.")
    
    # Validar que la foto guardada realmente contenga un rostro para evitar errores futuros
    try:
        if DeepFace:
            # Una detección rápida solo para verificar que haya una cara
            DeepFace.extract_faces(img_path=master_path, detector_backend="opencv")
        return {"success": True, "message": "Usuario registrado exitosamente en el sistema."}
    except Exception:
        if os.path.exists(master_path):
            os.remove(master_path)
        raise HTTPException(status_code=422, detail="No se detectó un rostro claro. Intenta registrarte con mejor luz.")

@app.post("/api/login")
async def login_user(payload: AuthRequest):
    """Compara la captura en vivo contra el rostro registrado para iniciar sesión."""
    if not DeepFace:
        raise HTTPException(status_code=503, detail="La librería DeepFace se está cargando o no está instalada.")

    master_path = os.path.join(REGISTERED_DIR, "user_master.jpg")
    if not os.path.exists(master_path):
        raise HTTPException(status_code=404, detail="No hay ningún usuario registrado en el sistema. Registrate primero.")

    # Guardar temporalmente la captura del intento de login
    temp_dir = os.path.join(DATA_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"login_{int(time.time() * 1000)}.jpg")

    if not save_base64_image(payload.image, temp_path):
        raise HTTPException(status_code=400, detail="Formato de imagen inválido.")

    start_time = time.time()
    try:
        # DeepFace.verify compara dos imágenes y calcula la distancia matemática de los vectores faciales
        verification = DeepFace.verify(
            img1_path=master_path,
            img2_path=temp_path,
            detector_backend="opencv",
            enforce_detection=True
        )

        inference_time = round(time.time() - start_time, 3)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # Extraemos el veredicto biométrico
        is_verified = bool(verification["verified"]) # True si es la misma persona
        distance = float(round(verification["distance"], 4)) # Menor distancia = mayor similitud
        threshold = float(verification["threshold"])

        if is_verified:
            return {
                "success": True,
                "access_granted": True,
                "message": "Acceso Concedido. Rostro verificado con éxito.",
                "metrics": {"distance": distance, "threshold": threshold, "time_seconds": inference_time}
            }
        else:
            return {
                "success": True,
                "access_granted": False,
                "message": "Acceso Denegado. El rostro no coincide con el usuario registrado.",
                "metrics": {"distance": distance, "threshold": threshold, "time_seconds": inference_time}
            }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        err_msg = str(e)
        if "Face could not be detected" in err_msg:
            raise HTTPException(status_code=422, detail="No se detectó ningún rostro en el intento de login.")
        raise HTTPException(status_code=500, detail=f"Error en el emparejamiento neuronal: {err_msg}")
