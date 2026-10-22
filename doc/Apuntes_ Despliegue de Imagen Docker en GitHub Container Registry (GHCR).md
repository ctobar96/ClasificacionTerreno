# Despliegue de Imagen Docker en GitHub Container Registry (GHCR)

**Proyecto:** Clasificador de Imágenes Satelitales (EuroSAT)  
**Entorno:** Ubuntu (WSL2)  
**Usuario GitHub:** ctobar96  

## Paso 1: Crear el filtro `.dockerignore`

En la raíz del proyecto (junto al `Dockerfile`), crear un archivo de texto llamado **`.dockerignore`** para evitar empaquetar el entorno virtual y los datos pesados de entrenamiento.
**Contenido del archivo:**

```text
.venv/
env/
data/
*.tfrecord
__pycache__/
.ipynb_checkpoints/
```

## Paso 2: Construir la imagen optimizada

Empaquetar la aplicación localmente ejecutando este comando en la terminal (asegurarse de incluir el punto al final):

```bash
docker build -t clasificador-eurosat:v1 .
```

## Paso 3: Autenticarse en el registro de GitHub

Conectar el motor de Docker local con los servidores de GHCR:

```bash
docker login ghcr.io -u ctobar96
```

*(Nota: Cuando la consola solicite el `Password:`, se debe pegar el Personal Access Token (PAT) que empieza con `ghp_...` y presionar Enter. Por seguridad, Linux no mostrará los caracteres mientras se pegan).*

## Paso 4: Etiquetar la imagen (Tagging)

Renombrar la imagen local para que coincida con la ruta de destino exacta en la cuenta de GitHub:

```bash
docker tag clasificador-eurosat:v1 ghcr.io/ctobar96/clasificador-eurosat:v1
```

## Paso 5: Subir el contenedor a la nube (Push)

Enviar el artefacto final hacia la sección "Packages" del repositorio en GitHub para que quede disponible para su posterior descarga en servidores (ej. AWS EC2):

```bash
docker push ghcr.io/ctobar96/clasificador-eurosat:v1
```