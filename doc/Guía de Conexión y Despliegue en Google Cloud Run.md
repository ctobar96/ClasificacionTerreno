# Guía de Conexión y Despliegue en Google Cloud Run (CLI / WSL2)

Esta guía documenta los pasos necesarios para conectar, configurar y desplegar la aplicación Streamlit con el modelo de Deep Learning en **Google Cloud Run** ejecutando los comandos directamente desde la terminal de WSL2.

---

### 1. Archivos Base del Proyecto

Antes de iniciar el despliegue, la raíz de tu proyecto debe contar con los siguientes tres archivos de configuración:

#### A. `Dockerfile`

```dockerfile
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false", \
     "--server.headless=true"]

```

#### B. Excepción de Modelo en `.gitignore`

Asegúrate de permitir que el modelo `.keras` de producción sea incluido al empaquetar el código fuente:

```text
# Bloquear todos los modelos pesados
*.keras
models/*

# Permitir exclusivamente el modelo de producción
!models/fine_tuned/
!models/fine_tuned/modelo_efnetb0_ft_final.keras

```

---

### 2. Autenticación y Configuración Inicial en GCP

Abre tu terminal en **WSL2** y ejecuta la secuencia de inicialización de `gcloud`:

```bash
# 1. Autenticarte con tu cuenta de Google Cloud (abre navegador)
gcloud auth login

# 2. Configurar el proyecto activo
gcloud config set project clasificacion-terreno-eurosat

# 3. Habilitar las APIs requeridas en el proyecto
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com

```

---

### 3. Configuración de Permisos IAM de Infraestructura

Otorga los permisos mínimos requeridos a la cuenta de servicio por defecto de Compute Engine para que Cloud Build pueda empaquetar y almacenar el contenedor:

```bash
# Permiso para leer artefactos de almacenamiento
gcloud projects add-iam-policy-binding clasificacion-terreno-eurosat \
    --member="serviceAccount:575655024196-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# Permiso para escribir logs de compilación
gcloud projects add-iam-policy-binding clasificacion-terreno-eurosat \
    --member="serviceAccount:575655024196-compute@developer.gserviceaccount.com" \
    --role="roles/logging.logWriter"

```

---

### 4. Comando de Despliegue a Producción

Para enviar el código fuente, compilar el contenedor en la nube y publicar el servicio en Google Cloud Run, ejecuta:

```bash
gcloud run deploy clasificador-eurosat \
  --source . \
  --region us-central1 \
  --port 8501 \
  --memory 2Gi \
  --cpu 1 \
  --allow-unauthenticated \
  --session-affinity

```

#### Parámetros explicados:

* **`--source .`**: Envía el directorio actual a Cloud Build para generar la imagen Docker usando el `Dockerfile` local.
* **`--memory 2Gi`**: Reserva 2 GB de RAM para soportar la carga del modelo TensorFlow y el procesamiento matricial.
* **`--port 8501`**: Expone el puerto por defecto del servidor web de Streamlit.
* **`--allow-unauthenticated`**: Genera una URL pública accesible desde cualquier navegador HTTPS.
* **`--session-affinity`**: Mantiene la conexión del usuario pegada a la misma instancia (útil para el estado interno de Streamlit).

---

### 5. Comandos de Operación y Monitoreo

| Operación | Comando en WSL2 |
| --- | --- |
| **Monitorear logs en vivo** | `gcloud run services logs tail clasificador-eurosat --region us-central1` |
| **Obtener URL del servicio** | `gcloud run services describe clasificador-eurosat --region us-central1 --format='value(status.url)'` |
| **Aumentar memoria/RAM** | `gcloud run services update clasificador-eurosat --memory 4Gi --region us-central1` |
| **Eliminar el servicio** | `gcloud run services delete clasificador-eurosat --region us-central1` |