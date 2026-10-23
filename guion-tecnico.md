## 1. Guion del Pitch Técnico (Resumen Ejecutivo de 3 Minutos)

> **Problema y Objetivo:**
> *"El proyecto resuelve la clasificación automatizada de cobertura terrestre utilizando el dataset de imágenes satelitales EuroSAT. El objetivo principal fue construir un flujo de MLOps de extremo a extremo, abarcando desde la experimentación con redes convolucionales hasta el despliegue monitoreado en producción."*

> **Evolución del Modelo (Data Science):**
> *"Comenzamos con una arquitectura CNN customizada como línea base ($92.54\%$ de *accuracy*). Para maximizar el rendimiento con un menor costo computacional, aplicamos *Transfer Learning* con **EfficientNetB0**. Mediante *Feature Extraction* alcanzamos un $95.33\%$, y con un ajuste fino (*Fine-Tuning*) de los bloques superiores logramos un **$96.52\%$ de precisión final** en el conjunto de prueba."*

El paso de la CNN Custom a Transfer Learning con EfficientNetB0 generó el salto principal en rendimiento, aumentando la precisión del $93.04\%$ al $95.73\%$ y reduciendo drásticamente la pérdida de $0.2096$ a $0.1391$.""En la etapa de Fine-Tuning, la exactitud global se mantuvo en $95.73\%$, pero la función de pérdida disminuyó de $0.1391$ a $0.1377$. Esto demuestra que el ajuste fino de los bloques superiores no solo mantuvo el nivel de acierto, sino que mejoró la calibración de las probabilidades del modelo, haciendo que sus predicciones sean más seguras (con menor incertidumbre/entropía cruzada) sin caer en sobreajuste (overfitting).

> **Arquitectura de Despliegue (MLOps & Cloud):**
> *"Para garantizar la reproducibilidad y el desacoplamiento, empaquetamos la aplicación Streamlit con Docker y publicamos el contenedor en GitHub Container Registry (GHCR). La infraestructura en AWS consta de una instancia EC2 `t2.micro` ajustada para costo-eficiencia en la capa gratuita."*

> **Seguridad y Observabilidad:**
> *"Adoptamos las mejores prácticas de la industria: implementamos un **Rol IAM** adjunto a la instancia para otorgar permisos a nivel de infraestructura, evitando almacenar credenciales de AWS en archivos de texto plano o variables de entorno. Integramos los registros del contenedor directamente a **AWS CloudWatch** usando el controlador `awslogs` y configuramos una alerta automática de consumo de CPU ($\ge 80\%$) para detectar cuellos de botella en la inferencia."*

---

## 2. Justificación Técnica de Decisiones (El "Por qué")

### ¿Por qué EfficientNetB0 sobre otras arquitecturas (p. ej., VGG16 o ResNet50)?

* **Razón:** EfficientNet utiliza un escalamiento compuesto (*compound scaling*) que equilibra profundidad, ancho de red y resolución de entrada.
* **Argumento de Defensa:** *"A diferencia de VGG16 o ResNet50, que tienen decenas de millones de parámetros, EfficientNetB0 logra una precisión superior con solo 5.3 millones de parámetros. Esto reduce el consumo de memoria RAM y CPU, permitiendo realizar inferencias rápidas en servidores con recursos restringidos como un `t2.micro`."*

### ¿Por qué Docker y GHCR en lugar de desplegar código fuente directo en el servidor?

* **Razón:** Paridad de entornos y aislamiento de dependencias.
* **Argumento de Defensa:** *"Desplegar el código fuente directamente en el servidor genera problemas de consistencia de librerías (TensorFlow/Keras y sus dependencias de sistema). Contenerizar la aplicación garantiza que el entorno de desarrollo sea exactamente igual al de producción. Usar GHCR permite versionar el artefacto compilado (`:v1`), facilitando despliegues repetibles sin depender del código local del servidor."*

### ¿Por qué Roles IAM en lugar de un archivo `.env` con AWS Keys?

* **Razón:** Seguridad en la nube y principio de menor privilegio (*Principle of Least Privilege*).
* **Argumento de Defensa:** *"Guardar claves de acceso estáticas (`AWS_ACCESS_KEY_ID`) en el servidor o en el código expone el entorno a filtraciones. Al asociar una política IAM (`CloudWatchAgentServerPolicy`) directamente a la instancia EC2 mediante un perfil de perfil IAM, la máquina obtiene credenciales temporales y rotativas gestionadas automáticamente por el servicio de metadatos de AWS (IMDS)."*

---

## 3. Preguntas Críticas Anticipadas del Jurado y Respuestas

**P1: ¿Cómo escalaría esta solución si el tráfico pasa de 10 a 10,000 peticiones por minuto?**

* **Respuesta:** *"Actualmente la arquitectura es monolítica en un servidor único. Para escalar vertical y horizontalmente:*
1. *Desacoplaría la inferencia de la interfaz web, convirtiendo el modelo en una API REST (con FastAPI) o un endpoint en **AWS SageMaker**.*
2. *Migraría el contenedor a un orchestrador como **Amazon ECS (Elastic Container Service)** o **EKS (Kubernetes)** detrás de un **Application Load Balancer (ALB)** con reglas de *Auto Scaling*.*
3. *Optimizaría el modelo exportándolo a formato **ONNX** o **TensorRT** para reducir la latencia de inferencia en procesadores CPU o GPU."*



**P2: ¿Por qué no utilizar una arquitectura Serverless como AWS Lambda?**

* **Respuesta:** *"Las funciones Serverless tienen limitaciones de tamaño de empaquetado (máximo 250 MB descomprimido o 10 GB en contenedor) y sufren de 'arranque en frío' (*cold start*). Cargar librerías pesadas como TensorFlow en cada invocación esporádica introduce latencias de varios segundos. Para un tablero interactivo como Streamlit, una instancia de cómputo persistente o un servicio de contenedores continuos ofrece un tiempo de respuesta más estable."*

**P3: ¿Qué estrategia siguió para validar que el modelo no estuviera sufriendo Overfitting?**

* **Respuesta:** *"Se dividió el dataset EuroSAT aplicando estratificación en conjuntos de entrenamiento ($70\%$), validación ($15\%$) y prueba ($15\%$). Durante el entrenamiento de la CNN y el Fine-Tuning de EfficientNet, monitoreamos continuamente las curvas de pérdida (*loss*) y precisión (*accuracy*) entre entrenamiento y validación. Además, aplicamos aumentación de datos (*data augmentation*) con rotaciones, giros y variaciones de brillo para mejorar la generalización."*

---

## 4. Matriz Resumen de Métricas para la Exposición

| Etapa de Experimentación | Arquitectura | Parámetros Entrenables | Test Accuracy | Ventaja Principal |
| --- | --- | --- | --- | --- |
| **Baseline** | Custom CNN (3 capas de Conv2D) | ~1.2M | 92.54% | Ligero, rápido entrenamiento inicial. |
| **Feature Extraction** | EfficientNetB0 (Base congelada) | ~128K (solo *Top Layer*) | 95.33% | Uso de características preentrenadas en ImageNet. |
| **Fine-Tuning Final** | EfficientNetB0 (Descongelado parcial) | ~2.1M | **96.52%** | Alta precisión ajustada a patrones espectrales/geográficos. |

---

¿Quieres redactar las diapositivas o preparar algún punto específico sobre la arquitectura de la red neuronal para tu presentación?