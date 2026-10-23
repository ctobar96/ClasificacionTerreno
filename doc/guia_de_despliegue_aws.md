# Guía de Despliegue en la Nube: AWS EC2, Docker y CloudWatch

Esta guía detalla el proceso paso a paso para desplegar una aplicación de Machine Learning (Streamlit) en Amazon Web Services (AWS). La arquitectura utiliza una instancia EC2 (Capa Gratuita), contenedores Docker alojados en GitHub Container Registry (GHCR) y Amazon CloudWatch para el monitoreo de logs y rendimiento.

---

## 1. Configuración de Seguridad: Crear el Rol IAM para CloudWatch

Antes de encender el servidor, es necesario otorgarle permisos a EC2 para que envíe métricas y logs a CloudWatch automáticamente sin exponer credenciales en el código.

1. Ve a la consola de AWS y busca el servicio **IAM**.
2. En el menú izquierdo, haz clic en **Roles** y luego en **Create role** (Crear rol).
3. Selecciona **AWS service** como tipo de entidad de confianza y elige **EC2** en el caso de uso. Haz clic en **Next**.
4. En el buscador de políticas, escribe `CloudWatchAgentServerPolicy`, marca la casilla correspondiente y haz clic en **Next**.
5. Asigna el nombre `Rol-EC2-CloudWatch` al rol y haz clic en **Create role**.

> **Verificación:** Ve a **IAM > Roles** y confirma que `Rol-EC2-CloudWatch` aparece en la lista.

---

## 2. Creación del Servidor: Lanzar la Instancia EC2

1. En la barra de búsqueda de AWS, escribe **EC2** y selecciona el servicio. Haz clic en el botón naranja **Launch instance** (Lanzar instancia).
2. **Nombre:** Ponle un nombre reconocible, por ejemplo: `Servidor-EuroSAT`.
3. **Imagen de SO (AMI):** Selecciona el logo de **Ubuntu** (Ubuntu Server 22.04 LTS o 24.04 LTS). Asegúrate de que tenga la etiqueta *Free tier eligible*.
4. **Tipo de instancia:** Déjalo en `t2.micro` (o `t3.micro` según tu región). Estas son las máquinas aptas para la capa gratuita.
5. **Par de claves (Key pair):** Haz clic en **Create new key pair**. Asígnale el nombre `llave-eurosat`, tipo **RSA** y formato **.pem**. Guarda muy bien el archivo descargado en tu computadora.
6. **Configuración de red (Network settings):**
   * Haz clic en el botón **Edit** (Editar).
   * Asegúrate de que **Auto-assign public IP** esté en **Enable**.
   * **Regla 1 (SSH):** Tipo `SSH`, Puerto `22`, Origen `Anywhere` (`0.0.0.0/0`).
   * **Regla 2 (Streamlit):** Haz clic en **Add security group rule**. Tipo `Custom TCP`, Puerto `8501`, Origen `Anywhere` (`0.0.0.0/0`). *(Esto permitirá el acceso web a la aplicación).*
7. **Detalles avanzados (Advanced details):**
   * Despliega la sección y en **IAM instance profile** selecciona el rol creado anteriormente: `Rol-EC2-CloudWatch`.
8. **Almacenamiento (Storage):** Cambia el tamaño de disco de 8 GB a **20 GB** (tipo `gp3`). La capa gratuita permite hasta 30 GB.
9. Revisa el resumen y haz clic en el botón naranja **Launch instance**.

> **Verificación:** En la sección **EC2 > Instances**, espera a que el estado de `Servidor-EuroSAT` cambie a **Running** (en verde) y anota la dirección **Public IPv4 address**.

---

## 3. Conexión SSH e Instalación de Docker

Abre tu terminal (por ejemplo, Ubuntu en WSL2) y navega hasta la carpeta donde guardaste tu archivo `.pem`.

**1. Conectarse a la instancia EC2:**
```bash
# Asignar permisos restringidos a la llave privada (solo la primera vez)
chmod 400 llave-eurosat.pem

# Conectarse al servidor (reemplaza TU_IP_PUBLICA por la IP de AWS)
ssh -i "llave-eurosat.pem" ubuntu@TU_IP_PUBLICA
```

**2. Instalar Docker y configurar permisos:**
Una vez dentro del servidor de Amazon (verás el prompt `ubuntu@ip-...`), ejecuta estos comandos:
```bash
# Actualizar repositorios e instalar Docker
sudo apt update && sudo apt install -y docker.io

# Iniciar y habilitar el servicio de Docker
sudo systemctl start docker
sudo systemctl enable docker

# Agregar el usuario ubuntu al grupo docker (evita usar sudo en cada comando)
sudo usermod -aG docker ubuntu
newgrp docker
```

> **Verificación:** Ejecuta `docker ps`. Debe responder una tabla vacía sin solicitar permisos de superusuario (`sudo`).

---

## 4. Despliegue con Logs Integrados en CloudWatch

Conectaremos el motor de Docker directamente con CloudWatch mediante el controlador nativo `awslogs`.

**1. Iniciar sesión en GHCR (Solo si el contenedor es Privado):**
Si tu imagen en GitHub es privada, utiliza este método para evitar errores de caracteres ocultos al pegar contraseñas en Linux:
```bash
echo "ghp_TU_TOKEN_AQUI" | docker login ghcr.io -u ctobar96 --password-stdin
```
*(Si tu contenedor es público, puedes omitir este paso).*

**2. Ejecutar la aplicación:**
Descarga y lanza el contenedor en segundo plano, redirigiendo el puerto 8501 y conectando los logs a la nube. *(Ajusta `us-east-1` por la región exacta de tu EC2 si es diferente)*:

```bash
docker run -d \
  -p 8501:8501 \
  --name eurosat-app \
  --log-driver=awslogs \
  --log-opt awslogs-region=us-east-1 \
  --log-opt awslogs-group=/aws/ec2/eurosat-app \
  --log-opt awslogs-create-group=true \
  --log-opt awslogs-stream=streamlit-instance \
  ghcr.io/ctobar96/clasificador-eurosat:v1
```

> **Verificación:** Abre tu navegador web e ingresa a `http://TU_IP_PUBLICA:8501`. Si la interfaz carga correctamente, el flujo de despliegue MLOps se ha completado con éxito.

---

## 5. Monitoreo y Alertas en CloudWatch

### Visualizar los logs de la aplicación
1. En la consola de AWS, busca el servicio **CloudWatch**.
2. En el menú izquierdo, ve a **Logs > Log groups**.
3. Selecciona el grupo `/aws/ec2/eurosat-app` y haz clic en la secuencia `streamlit-instance`.
4. Verás las impresiones de consola y registros de inferencia de tu modelo en tiempo real.

### Crear una Alarma de Consumo de CPU
Para monitorear el rendimiento del modelo (EfficientNet) y evitar saturar la capa gratuita:
1. En CloudWatch, ve a **Alarms > All alarms** y haz clic en **Create alarm**.
2. Haz clic en **Select metric** y navega a: **EC2 > Per-Instance Metrics**.
3. Selecciona la métrica `CPUUtilization` correspondiente a tu instancia `Servidor-EuroSAT` y haz clic en **Select metric**.
4. En las condiciones de la alarma configura:
   * **Threshold type:** Static.
   * **Whenever CPUUtilization is...:** Greater/Equal (`>=`).
   * **than...:** `80` (80%).
5. Haz clic en **Next**, deja las acciones por defecto y asigna el nombre `Alerta-CPU-EuroSAT`.
6. Haz clic en **Create alarm**.

> **Nota de Mantenimiento:** Como estrategia eficiente para proyectos de portafolio, se recomienda mantener el servidor apagado (Estado: *Stopped*) cuando no se esté utilizando, y encenderlo únicamente para pruebas o demostraciones.