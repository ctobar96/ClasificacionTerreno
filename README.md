# EuroSAT Land Cover Classification: Custom CNN & EfficientNetB0 Transfer Learning

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Project Status](https://img.shields.io/badge/Status-Completed-brightgreen.svg)]()
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![GCP](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4?style=flat&logo=google-cloud&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=flat&logo=github-actions&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?style=flat&logo=terraform&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=flat&logo=streamlit&logoColor=white)

## Descripción del Proyecto
Este repositorio contiene el código fuente, la contenerización, la automatización CI/CD y la infraestructura como código (IaC) para un modelo de clasificación de imágenes satelitales (dataset EuroSAT). Este proyecto fue desarrollado como parte integral de mi **Magíster en Data Science**, demostrando el ciclo de vida completo de Machine Learning (MLOps): desde el entrenamiento e ingeniería de características hasta su puesta en producción en **Google Cloud Run** con despliegue automatizado mediante **GitHub Actions**.

---

## Resumen Ejecutivo y Resultados

El objetivo metodológico del proyecto consistió en establecer una línea base (*Baseline*) sólida mediante una arquitectura propia, identificar sus cuellos de botella algorítmicos en la extracción de características y superarlos progresivamente mediante transferencia de conocimiento preentrenado en ImageNet.

| Fase / Experimento | Arquitectura | Resolución Entrada | Exactitud (Accuracy) | Pérdida (Test Loss) |
| :--- | :--- | :---: | :---: | :---: |
| **1. Baseline (Custom)** | CNN Profunda (32-64-128) + SpatialDropout | 64x64 | **93.04%** | **0.2096** |
| **2. Feature Extraction** | EfficientNetB0 (Pesos congelados) | 128x128 | **95.73%** | **0.1391** |
| **3. Fine-Tuning** | EfficientNetB0 (Ajuste Fino Capas Top) | 128x128 | **95.73%** | **0.1377** |

---

## Principales Hallazgos Técnicos

1. **Superación del Baseline:** La CNN personalizada alcanzó un rendimiento sobresaliente (~92.5%) utilizando regularización espacial (`SpatialDropout2D`), `BatchNormalization` y `GlobalAveragePooling2D`.
2. **Resolución del Cuello de Botella Agrícola:** La CNN propia presentó ligeras dificultades para diferenciar microtexturas en clases con alta similitud espectral/visual (`HerbaceousVegetation` vs `PermanentCrop`).
3. **Escalado de Resolución (128x128):** Para evitar la degradación espacial del mapa de características en EfficientNetB0, se adaptó el pipeline (`tf.data`) interpolando las imágenes de 64x64 a 128x128.
4. **Impacto del Fine-Tuning:** Descongelar los bloques convolucionales superiores con un *Learning Rate* reducido (`1e-5`) redujo la función de pérdida a **0.1377**, aumentando sustancialmente la certeza de las predicciones.

---

## Estructura del Repositorio

El proyecto sigue una arquitectura estandarizada MLOps basada en *Cookiecutter Data Science*:

```text
ClasificacionTerreno/
│
├── .github/
│   └── workflows/
│       └── deploy.yml       # Pipeline CI/CD automatizado para Cloud Run
│
├── terraform/               # Infraestructura como Código (IaC)
│   ├── provider.tf          # Configuración de GCP y Backend remoto GCS
│   ├── main.tf              # Definición de IAM, APIs y Cloud Run
│   ├── variables.tf         # Parámetros del proyecto y región
│   └── outputs.tf           # Salida de URLs y Service Accounts
│
├── data/                    # Datos crudos y procesados (.tfrecord / imágenes)
│   ├── raw/
│   └── processed/
│
├── doc/                     # Documentación técnica de arquitectura y despliegue
│   ├── Apuntes_ Despliegue de Imagen Docker en GitHub Container Registry (GHCR).md
│   └── guia_de_despliegue_aws.md
│   └── img        
│
├── models/                  # Pesos guardados en formato Keras (.keras)
│   ├── baselines/           # modelo_cnn_custom.keras (92.54%)
│   ├── feature_extraction/  # modelo_efnetb0_fe.keras (95.33%)
│   └── fine_tuned/          # modelo_efnetb0_ft_final.keras (96.52%)
│
├── logs/                    # Historiales de entrenamiento (.json, .csv)
│   └── histories/
│
├── reports/                 # Artefactos de evaluación y gráficos
│   ├── figures/             # Matrices de confusión y curvas de aprendizaje
│   └── summaries/           # Reportes de clasificación detallados (Precision/Recall/F1)
│
├── notebooks/               # Flujo experimental secuencial en Jupyter
│   ├── 01_eda_eurosat.ipynb
│   ├── 02_cnn_baseline.ipynb
│   └── 03_transfer_learning_efficientnet.ipynb
│
├── src/                     # Código modular y reutilizable
│   ├── data_loader.py       # Tubería tf.data y adaptadores de resolución
│   ├── models.py            # Definición de arquitecturas Keras
│   └── evaluate.py          # Generación de métricas globales y matrices de confusión
│
├── app.py                   # Dashboard web interactivo en Streamlit
├── Dockerfile               # Contenerización para entorno serverless
├── .gitignore               # Filtrado de modelos pesados y secretos IAM
├── README.md
└── requirements.txt         # Dependencias del proyecto
```

---

## Arquitectura y Tecnologías
La solución está construida bajo un enfoque de MLOps & cloud-native, asegurando replicabilidad, seguridad e infraestructura automatizada:

- **Modelado Deep Learning:** Redes neuronales convolucionales (CNN) y Transfer Learning utilizando EfficientNetB0 mediante TensorFlow y Keras.

- **Interfaz Web:** Aplicación interactiva construida con Streamlit para inferencia en tiempo real.

- **Contenerización:** Empaquetado optimizado con python:`3.10-slim` y compilación serverless en la nube con Cloud Build y Artifact Registry.

- **Infraestructura Cloud (GCP):** Despliegue serverless en Google Cloud Run (`us-central1`, 2GiB RAM, 1 CPU, escalado a cero y afinidad de sesión activa).

- **Integración y Despliegue Continuo (CI/CD):** Pipeline automatizado con GitHub Actions usando autenticación IAM segura mediante GitHub Secrets (`GCP_SA_KEY`).

- **Infraestructura como Código (IaC):** Gestión declarativa con Terraform y estado remoto centralizado con candado de concurrencia en Google Cloud Storage (GCS).

## Despliegue y CI/CD (Producción)
La aplicación está diseñada para ser desplegada rápidamente en cualquier servidor en la nube que tenga Docker instalado, sin necesidad de transferir el código fuente manualmente.

Para ver la guía paso a paso de cómo configurar la infraestructura en AWS Amazon EC2, asignar roles de CloudWatch y ejecutar el contenedor, consulta el archivo de documentación:
👉 **[Ver Guía de Despliegue en AWS](doc/guia_de_despliegue_aws.md)**

### Comando de ejecución rápida
Si ya cuentas con un servidor configurado, puedes levantar la aplicación con un solo comando:
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
*(Nota: Ajusta la región `us-east-1` según tu configuración en AWS).*

## 💻 Uso Local

Si deseas correr este proyecto en tu máquina local para desarrollo:

1. Clona este repositorio:
```bash
git clone https://github.com/ctobar96/ClasificacionTerreno.git
cd ClasificacionTerreno
```
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```


3. Ejecuta la aplicación de Streamlit:
```bash
streamlit run app.py
```

## 👨‍💻 Autor

**Cristian Tobar Morales**  
*Data Scientist | Analytics Engineer | ML Engineer*


### 🔗 Contacto

* **LinkedIn:** [Cristian Tobar Morales](#)
* **GitHub:** [@ctobar96](https://github.com/ctobar96)

---
## 📜 Licencia

Este proyecto se distribuye bajo la **licencia MIT**. Consulta el archivo `LICENSE` para más detalles.

