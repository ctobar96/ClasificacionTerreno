### Arquitectura Actual vs. Arquitectura Futura (Serverless)

#### 1. Arquitectura Actual (Prototipo Monolítico en EC2)

Todo el sistema (interfaz gráfica e inferencia del modelo) se ejecuta dentro de un único proceso y contenedor Docker cargado en la instancia virtual EC2.

```text
[ USUARIO / NAVEGADOR ]
          │
          │ HTTP (Puerto 8501)
          ▼
+------------------------------------------------------------------+
|                    INSTANCIA AWS EC2 (t2.micro)                  |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |             CONTENEDOR DOCKER (GHCR :v1)                   |  |
|  |                                                            |  |
|  |  +---------------------+        +-----------------------+  |  |
|  |  | Streamlit Frontend  | <----> | TensorFlow / Keras    |  |  |
|  |  | (Interfaz de usuario|        | (EfficientNetB0 .keras)|  |  |
|  |  +---------------------+        +-----------------------+  |  |
|  +------------------------------------------------------------+  |
|                                |                                 |
+--------------------------------|---------------------------------+
                                 | Controlador `awslogs`
                                 │ (Permisos vía Rol IAM)
                                 ▼
+------------------------------------------------------------------+
|                          AWS CLOUDWATCH                          |
|  • Logs: /aws/ec2/eurosat-app                                    |
|  • Métricas y Alarma: Alerta-CPU-EuroSAT (>= 80%)                |
+------------------------------------------------------------------+

```

---

#### 2. Arquitectura Futura (Propuesta de Producción Serverless & Desacoplada)

Separación del Frontend (interfaz) y Backend (motor de inferencia), utilizando un modelo optimizado en formato ONNX para eliminar la dependencia pesada de TensorFlow.

```text
[ USUARIO / NAVEGADOR ]
          │
          │ Carga de interfaz web
          ▼
+------------------------------------------------------------------+
|                   FRONTEND (UI INTERACTIVA)                      |
|      Streamlit / React alojado en AWS S3 + Amazon CloudFront     |
+------------------------------------------------------------------+
          │
          │ Petición HTTP POST (Imagen en Base64 / Multipart)
          ▼
+------------------------------------------------------------------+
|                       AMAZON API GATEWAY                         |
|                   Endpoint REST: /v1/predict                     |
+------------------------------------------------------------------+
          │
          │ Invocación por evento
          ▼
+------------------------------------------------------------------+
|                   AWS LAMBDA (BACKEND SERVERLESS)                |
|  • Imagen Docker reducida (< 500 MB)                             |
|  • Motor de inferencia: ONNX Runtime (sin TensorFlow)            |
|  • Modelo: EfficientNetB0 (.onnx) cuantizado a INT8              |
|  • Tiempo de ejecución efímero (Costo $0 en inactividad)         |
+------------------------------------------------------------------+
          │
          │ Telemetría automática
          ▼
+------------------------------------------------------------------+
|                          AWS CLOUDWATCH                          |
|  • Métricas Serverless (Invocaciones, Latencia, Errores 4xx/5xx)  |
+------------------------------------------------------------------+

```

---

### Puntos Técnicos para la Diapositiva de "Trabajos Futuros"

Para argumentar este diagrama en tu presentación de defensa, utiliza estos 3 pilares de ingeniería MLOps:

1. **Optimización del Modelo (*Model Compression*):**
* Conversión del modelo `.keras` a formato **ONNX** o **TensorFlow Lite (TFLite)** con cuantización a enteros de 8 bits (`INT8`). Esto reduce el peso del artefacto de ~30 MB a menos de 10 MB y disminuye la latencia de inferencia en CPU a menos de 100 ms.


2. **Desacoplamiento y Microservicios:**
* La interfaz de usuario no compite por memoria RAM con el motor de inferencia. Si la interfaz falla o cambia de diseño, el endpoint de predicción sigue funcionando sin interrupciones.


3. **Eficiencia Operativa y Financiera:**
* **Costo $0 cuando no hay uso:** La arquitectura pasa de un cobro por hora fija (EC2) a un modelo $100\%$ basado en demanda (*Pay-per-use*).
* **Escalabilidad Elástica:** AWS Lambda puede responder de forma simultánea a 1 o a 1,000 peticiones en paralelo sin necesidad de configurar balanceadores de carga (*Load Balancers*) ni reglas manuales de autoescalado.

------


## **Propuesta de Arquitectura Desacoplada y Serverless (Trabajos Futuros)**

Para escalar el modelo de clasificación de cobertura terrestre EuroSAT y llevarlo a un entorno de producción masivo, se propone la evolución del sistema desde un enfoque monolítico basado en instancias dedicadas hacia una arquitectura de microservicios, totalmente desacoplada y orientada a eventos (*Serverless*).

### 1. Separación de Responsabilidades (Frontend y Backend)

El diseño actual acopla la interfaz de usuario interactiva y el motor de inferencia de aprendizaje profundo dentro de un mismo contenedor. La arquitectura futura divide el sistema en dos capas independientes:

* **Capa de Presentación (Frontend Estático):** La interfaz gráfica se migrará a un framework ligero alojado en **Amazon S3** y distribuido globalmente mediante la red de entrega de contenido (CDN) **Amazon CloudFront**. Esto elimina por completo el consumo de cómputo para mantener la interfaz web activa.
* **Capa de Lógica (API REST):** Las imágenes satelitales ingresadas por el usuario se enviarán a través de peticiones HTTP POST hacia un **Amazon API Gateway**, el cual actuará como un enrutador seguro para desencadenar la inferencia.

### 2. Optimización del Modelo (Model Compression)

El uso de librerías completas como TensorFlow o Keras resulta ineficiente para inferencias transaccionales debido a su alto consumo de memoria RAM y tiempos de inicialización. Para habilitar el uso de cómputo efímero, se implementarán técnicas de compresión:

* **Exportación a ONNX:** Los pesos de la red neuronal EfficientNetB0 (que actualmente alcanzan un 96.52% de exactitud tras el *Fine-Tuning*) se convertirán al estándar abierto ONNX. La inferencia se ejecutará utilizando **ONNX Runtime**, lo que reduce el tamaño de las dependencias de cientos de megabytes a unos pocos megabytes.
* **Cuantización INT8:** Se aplicará una reducción de precisión matemática de punto flotante de 32 bits (FP32) a enteros de 8 bits (INT8). Esto comprimirá el tamaño físico del modelo en disco en aproximadamente un 75% y acelerará los tiempos de predicción en procesadores CPU de manera significativa, asumiendo un *trade-off* con una pérdida empíricamente marginal en la exactitud global.

### 3. Inferencia Serverless con AWS Lambda

El motor de inferencia se desplegará utilizando **AWS Lambda**, empaquetado en una imagen de contenedor Docker optimizada.

* **Mitigación del Arranque en Frío (*Cold Start*):** Al prescindir de TensorFlow y utilizar ONNX, el contenedor de Lambda podrá inicializarse en milisegundos y cargar el modelo en memoria casi instantáneamente.
* **Escalabilidad Elástica:** AWS Lambda procesará cada imagen entrante en un entorno de ejecución aislado. Esto permitirá al sistema escalar automáticamente de cero a miles de ejecuciones concurrentes sin necesidad de aprovisionar infraestructura, configurar grupos de autoescalado o gestionar balanceadores de carga.
* **Eficiencia Financiera:** La infraestructura transicionará de un modelo de costos fijos por hora (EC2) a un modelo estricto de pago por uso (*Pay-per-use*), garantizando un gasto operativo de cero dólares durante los períodos de inactividad de la aplicación.

### 4. Telemetría y Observabilidad Continua

La integración nativa de API Gateway y Lambda con **AWS CloudWatch** permitirá un monitoreo granular del nuevo flujo de trabajo. Se registrarán métricas específicas de latencia de inferencia en milisegundos, tasas de error (HTTP 4xx y 5xx) y volumen de invocaciones, manteniendo la trazabilidad completa del ciclo de vida MLOps en producción.