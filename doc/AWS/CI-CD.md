Para implementar la Integración y Despliegue Continuo (CI/CD) en tu proyecto utilizando GitHub Actions, necesitas conectar de forma segura tu repositorio con tu servidor EC2 y crear un archivo de automatización.

**1. Configurar los Secretos en GitHub**
GitHub necesita credenciales para entrar a tu servidor EC2 sin exponerlas al público. Ve a tu repositorio en GitHub > **Settings** > **Secrets and variables** > **Actions** > **New repository secret**. Añade estos tres:

* `EC2_HOST`: La dirección IP pública de tu servidor (ej. `54.123.45.67`).
* `EC2_USERNAME`: El usuario de tu máquina (por defecto en Ubuntu es `ubuntu`).
* `EC2_SSH_KEY`: Pega aquí todo el contenido de tu archivo `.pem` (incluyendo las líneas que dicen `BEGIN` y `END`).

**2. Crear el archivo del Workflow**
En tu máquina local (dentro de la carpeta de tu proyecto `ClasificacionTerreno`), crea una carpeta oculta llamada `.github`, dentro de ella otra llamada `workflows`, y crea un archivo llamado `deploy.yml`. La ruta exacta debe ser: `.github/workflows/deploy.yml`.

**3. Escribir el Pipeline (El código de automatización)**
Copia y pega este código en `deploy.yml`. Este script le dice a GitHub que construya la imagen, la suba a GHCR y luego entre por SSH a tu EC2 para actualizar el contenedor utilizando tu configuración exacta de CloudWatch.

```yaml
name: MLOps CI/CD Pipeline

on:
  push:
    branches: [ "main" ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - name: Check out the repo
        uses: actions/checkout@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ghcr.io/ctobar96/clasificador-eurosat:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USERNAME }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            docker pull ghcr.io/ctobar96/clasificador-eurosat:latest
            docker stop eurosat-app || true
            docker rm eurosat-app || true
            docker run -d -p 8501:8501 --name eurosat-app \
              --log-driver=awslogs \
              --log-opt awslogs-region=us-east-1 \
              --log-opt awslogs-group=/aws/ec2/eurosat-app \
              --log-opt awslogs-create-group=true \
              --log-opt awslogs-stream=streamlit-instance \
              ghcr.io/ctobar96/clasificador-eurosat:latest

```

**4. Activar la automatización**
Guarda el archivo y súbelo a tu repositorio principal:

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: implementar pipeline MLOps con GitHub Actions"
git push origin main

```

Desde ese momento, cada vez que hagas un `git push` con cambios en tu código o modelo, ve a la pestaña **Actions** en tu repositorio de GitHub. Verás la ejecución en vivo del flujo automatizado que construirá la nueva versión y la desplegará en tu servidor AWS EC2 sin que tengas que intervenir manualmente.