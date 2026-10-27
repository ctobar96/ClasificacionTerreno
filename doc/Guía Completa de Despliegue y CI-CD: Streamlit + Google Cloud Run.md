## Guía Completa de Despliegue y CI/CD: Streamlit + Google Cloud Run

Esta es la documentación técnica paso a paso para configurar, desplegar y automatizar la aplicación de clasificación de terreno (EuroSAT / EfficientNetB0) en Google Cloud Run usando GitHub Actions.

---

### Paso 1: Configurar excepciones en `.gitignore`

Para permitir que el archivo de flujo de trabajo (`.github/workflows/deploy.yml`) y el modelo de producción (`modelo_efnetb0_ft_final.keras`) sean rastreados por Git y subidos a la nube sin incluir archivos temporales ni otros modelos pesados, tu archivo `.gitignore` debe incluir las siguientes excepciones:

```text
# ==========================================
# Entornos virtuales
# ==========================================
.venv/
venv/
env/
ENV/

# ==========================================
# Variables de entorno y secretos
# ==========================================
.env
.env.*
!.env.example
*.key
*.pem
secrets/
credentials/
gcp-key.json

# ==========================================
# Python & Jupyter
# ==========================================
__pycache__/
*.py[cod]
*$py.class
*.so
.ipynb_checkpoints/

# ==========================================
# TensorFlow / Keras (Excepción de Modelo)
# ==========================================
*.h5
*.hdf5
*.ckpt
checkpoint/
checkpoints/

# Ignorar modelos genéricos pero permitir el de producción
*.keras
!models/fine_tuned/modelo_efnetb0_ft_final.keras

models/*
!models/fine_tuned/
models/fine_tuned/*
!models/fine_tuned/modelo_efnetb0_ft_final.keras

saved_model/
saved_models/

# ==========================================
# GitHub Workflows (Permitir CI/CD)
# ==========================================
!.github/
!.github/workflows/
!.github/workflows/deploy.yml

```

---

### Paso 2: Configurar la Cuenta de Servicio y Permisos en GCP (IAM)

Abre tu terminal en WSL2 e inicializa las políticas de acceso IAM para la cuenta por defecto y para la cuenta de servicio de GitHub Actions:

```bash
# 1. Otorgar permisos a la cuenta de cómputo por defecto para Cloud Build
gcloud projects add-iam-policy-binding clasificacion-terreno-eurosat \
    --member="serviceAccount:575655024196-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding clasificacion-terreno-eurosat \
    --member="serviceAccount:575655024196-compute@developer.gserviceaccount.com" \
    --role="roles/logging.logWriter"

# 2. Crear la cuenta de servicio dedicada para GitHub Actions
gcloud iam service-accounts create github-actions-deployer \
    --display-name="GitHub Actions Deployer"

# 3. Asignar roles necesarios a la cuenta de servicio de GitHub Actions
gcloud projects add-iam-policy-binding clasificacion-terreno-eurosat \
    --member="serviceAccount:github-actions-deployer@clasificacion-terreno-eurosat.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding clasificacion-terreno-eurosat \
    --member="serviceAccount:github-actions-deployer@clasificacion-terreno-eurosat.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding clasificacion-terreno-eurosat \
    --member="serviceAccount:github-actions-deployer@clasificacion-terreno-eurosat.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding clasificacion-terreno-eurosat \
    --member="serviceAccount:github-actions-deployer@clasificacion-terreno-eurosat.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding clasificacion-terreno-eurosat \
    --member="serviceAccount:github-actions-deployer@clasificacion-terreno-eurosat.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

```

---

### Paso 3: Generar Llave de Seguridad e Inyectar en GitHub Secrets

1. **Generar la clave JSON localmente:**
```bash
gcloud iam service-accounts keys create gcp-key.json \
    --iam-account=github-actions-deployer@clasificacion-terreno-eurosat.iam.gserviceaccount.com

```


2. **Copiar contenido:**
```bash
cat gcp-key.json

```


3. **Configurar en GitHub:**
* Navega a tu repositorio en **GitHub** > **Settings** > **Secrets and variables** > **Actions**.
* Haz clic en **New repository secret**.
* **Nombre:** `GCP_SA_KEY`
* **Valor:** Pega todo el contenido JSON copiado.


4. **Eliminar la clave local por seguridad:**
```bash
rm gcp-key.json

```



---

### Paso 4: Crear el Workflow de CI/CD (`deploy.yml`)

Crea la estructura de carpetas y el archivo `.github/workflows/deploy.yml`:

```bash
mkdir -p .github/workflows
touch .github/workflows/deploy.yml

```

Pega el siguiente código dentro de `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

jobs:
  deploy:
    name: Deploy to Google Cloud Run
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy clasificador-eurosat \
            --source . \
            --region us-central1 \
            --port 8501 \
            --memory 2Gi \
            --cpu 1 \
            --allow-unauthenticated \
            --session-affinity

```

---

### Paso 5: Despliegue Automático mediante Git

Para gatillar una nueva compilación y despliegue automático hacia producción, ejecuta:

```bash
git add .
git commit -m "ci: automatizacion de despliegue a Cloud Run finalizada"
git push origin main

```

---

### Paso 6: Verificación y Diagnóstico

| Acción | Comando / Recurso |
| --- | --- |
| **URL de Producción** | `[https://clasificador-eurosat-575655024196.us-central1.run.app](https://clasificador-eurosat-575655024196.us-central1.run.app)` |
| **Ver Logs en Tiempo Real** | `gcloud run services logs tail clasificador-eurosat --region us-central1` |
| **Monitorear Pipeline** | Pestaña **Actions** en tu repositorio de GitHub |