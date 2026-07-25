## 🛠️ Instalación y Arranque Automático

Sigue estos pasos en tu terminal para poner en marcha el sistema:

### 1. Navegar al Proyecto
```bash
cd computerV
```

### 2. Arrancar
```bash
./start.sh
```
*Este script crea el entorno virtual, instala dependencias y levanta el servidor.*

### 3. Acceder
Abre tu navegador en: 👉 **http://127.0.0.1:8000**

---

## 💻 Guía de Evaluación (Flujo de Pruebas sin Cámara)
La interfaz permite cargar imágenes (`.jpg`/`.png`) para simular el reconocimiento:

1.  **Registro:** Carga una foto y presiona **"1. Registrar Rostro Maestro"**.
2.  **Acceso Éxito:** Carga una foto de la misma persona y presiona **"2. Intentar Inicio de Sesión"**.
3.  **Acceso Denegado:** Carga una foto de otra persona para probar la seguridad.
