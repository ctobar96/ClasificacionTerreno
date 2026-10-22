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


## Cómo verificar tu contenedor en GitHub
Para confirmar visualmente que tu artefacto MLOps está listo, haz lo siguiente:

1. Ve a tu perfil de GitHub en el navegador: https://github.com/ctobar96

2. En el menú superior de tu perfil (donde dice Overview, Repositories, Projects), haz clic en la pestaña Packages (Paquetes).

3. ¡Ahí deberías ver tu contenedor clasificador-eurosat etiquetado como la versión v1!

(*Opcional: Si entras a ese paquete, en la configuración lateral a la derecha puedes conectarlo a tu repositorio de **ClasificacionTerreno** para que aparezca directamente en la página principal de tu código*).



## Cuando tu token expire

Cuando tu token expire (ya sea en 30 o 90 días), lo notarás porque al intentar ejecutar un comando de Docker (como hacer `push` de una nueva versión o `pull` para descargarla en AWS) la consola te devolverá un error de `unauthorized` o `denied`.

Para solucionarlo, debes seguir estos 3 sencillos pasos:

1. **Generar un nuevo token:**
Ve a tu cuenta de GitHub y sigue la misma ruta: *Settings -> Developer Settings -> Personal access tokens (classic)*. Genera un token nuevo marcando exactamente las mismas casillas (`write:packages` y `repo`).  
*(Opcional: puedes eliminar el token viejo de esa lista con el botón de la papelera para mantener el orden).*

2. **Cerrar la sesión caducada:**
En tu terminal de Ubuntu (WSL), debes limpiar la credencial antigua que quedó guardada en la memoria ejecutando este comando:

    ```bash
    docker logout ghcr.io
    ```

3. **Iniciar sesión con la nueva clave:**
Vuelve a conectarte usando tu usuario y pega el nuevo token cuando te pida el Password:

    ```bash
    docker login ghcr.io -u ctobar96
    ```

