# 🛰️ EuroSAT Land Cover Classification: Custom CNN & EfficientNetB0 Transfer Learning

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Project Status](https://img.shields.io/badge/Status-Completed-brightgreen.svg)]()

Este repositorio contiene la implementación end-to-end para la clasificación de cobertura terrestre (*Land Cover Classification*) sobre el dataset **EuroSAT**, desarrollada como parte de un proyecto de Magíster. 

El trabajo abarca desde el diseño, optimización y entrenamiento de una red neuronal convolucional personalizada (Custom CNN) hasta la aplicación de técnicas avanzadas de **Transfer Learning** y **Fine-Tuning** con **EfficientNetB0**, logrando superar la barrera del **96.5% de exactitud**.

---

## 📌 Resumen Ejecutivo y Resultados

El objetivo metodológico del proyecto consistió en establecer una línea base (*Baseline*) sólida mediante una arquitectura propia, identificar sus cuellos de botella algorítmicos en la extracción de características y superarlos progresivamente mediante transferencia de conocimiento preentrenado en ImageNet.

| Fase / Experimento | Arquitectura | Resolución Entrada | Exactitud (Accuracy) | Pérdida (Test Loss) |
| :--- | :--- | :---: | :---: | :---: |
| **1. Baseline (Custom)** | CNN Profunda (32-64-128) + SpatialDropout | 64x64 | **92.54%** | **0.2232** |
| **2. Feature Extraction** | EfficientNetB0 (Pesos congelados) | 128x128 | **95.33%** | **0.1656** |
| **3. Fine-Tuning** | EfficientNetB0 (Ajuste Fino Capas Top) | 128x128 | **96.52%** | **0.1154** |

---

## 📊 Principales Hallazgos Técnicos

1. **Superación del Baseline:** La CNN personalizada alcanzó un rendimiento sobresaliente (~92.5%) utilizando regularización espacial (`SpatialDropout2D`), `BatchNormalization` y `GlobalAveragePooling2D`.
2. **Resolución del Cuello de Botella Agrícola:** La CNN propia presentó ligeras dificultades para diferenciar microtexturas en clases con alta similitud espectral/visual (`HerbaceousVegetation` vs `PermanentCrop`).
3. **Escalado de Resolución (128x128):** Para evitar la degradación espacial del mapa de características en EfficientNetB0, se adaptó el pipeline (`tf.data`) interpolando las imágenes de 64x64 a 128x128.
4. **Impacto del Fine-Tuning:** Descongelar los bloques convolucionales superiores con un *Learning Rate* reducido (`1e-5`) redujo la función de pérdida a **0.1154**, aumentando sustancialmente la certeza de las predicciones.

---

## 📁 Estructura del Repositorio

El proyecto sigue una arquitectura estandarizada MLOps basada en *Cookiecutter Data Science*:

```text
ClasificacionTerreno/
│
├── data/                    # Datos crudos y procesados (.tfrecord / imágenes)
│   ├── raw/
│   └── processed/
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
├── app/                     # Interfaz web interactiva para inferencia
│   └── app.py               # Dashboard en Streamlit
│
├── .gitignore
├── Dockerfile               # Contenerización para despliegue
├── README.md
└── requirements.txt         # Dependencias del proyecto
```

---

## 🛠️ Tecnologías y Herramientas

* **Lenguaje:** Python 3.10+
* **Deep Learning Framework:** TensorFlow 2.x / Keras
* **Procesamiento e Infraestructura:** NumPy, Pandas, Scikit-learn, Google Colab GPU
* **Visualización:** Matplotlib, Seaborn
* **Despliegue & MLOps:** Streamlit, Docker, Git/GitHub

---

## 🚀 Instalación y Uso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/ClasificacionTerreno.git
cd ClasificacionTerreno
```

### 2. Crear Entorno Virtual e Instalar Dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ejecutar Evaluación de Modelos
```bash
python src/evaluate.py --model models/fine_tuned/modelo_efnetb0_ft_final.keras
```

### 4. Lanzar la Aplicación Interactiva (Streamlit)
```bash
streamlit run app/app.py
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

