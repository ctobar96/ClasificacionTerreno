# Clasificación de Imágenes Satelitales (EuroSAT) con Deep Learning 🌍🛰️

Este proyecto implementa un modelo de Red Neuronal Convolucional (CNN) para clasificar imágenes satelitales en 10 categorías distintas de uso de suelo (bosques, ríos, autopistas, zonas residenciales, etc.). Se utiliza el dataset **EuroSAT** procesado enteramente desde almacenamiento local mediante un pipeline de datos altamente optimizado.

## 📌 Objetivos del Proyecto
* Construir un clasificador de imágenes multiclase robusto y eficiente.
* Procesar datos de forma nativa desde archivos `.tfrecord` locales utilizando la API `tf.data`, asegurando una lectura por lotes (*batches*) que previene el colapso de la memoria RAM.
* Implementar un flujo de preprocesamiento de datos riguroso para evitar la fuga de información (*data leakage*), dividiendo matemáticamente los conjuntos en Entrenamiento, Validación y Prueba.
* Mitigar el sobreajuste (*overfitting*) combinando aumento de datos (*Data Augmentation*) con técnicas de regularización estructurales.

## 🏗️ Arquitectura y Tecnologías
* **Lenguaje:** Python
* **Framework Principal:** TensorFlow / Keras
* **Manipulación y Visualización:** Matplotlib, NumPy
* **Pipeline de Datos:** `tf.data.TFRecordDataset` (Lectura en disco, mapeo de funciones, paralelismo y *prefetching*).

**Estructura del Modelo (CNN):**
El modelo fue diseñado priorizando la eficiencia computacional (menos de 30,000 parámetros entrenables) sin sacrificar la capacidad de extracción de características:
1. **Bloques Convolucionales:** Dos capas `Conv2D` (32 y 64 filtros de 3x3) acompañadas de `BatchNormalization`, `MaxPooling2D` y `SpatialDropout2D` para consolidar el aprendizaje de patrones espaciales y texturas complejas.
2. **Global Average Pooling:** Transición eficiente que reemplaza al clásico `Flatten`, promediando los mapas de características y reduciendo la carga en memoria en más de un 95%.
3. **Clasificación Densa:** Capa oculta de 128 neuronas con regularización *L2 (Ridge)* y *Dropout (0.5)*, finalizando en una capa `Softmax` de 10 salidas.

## ⚙️ Configuración del Entorno y Reproducción

1. **Clonar el repositorio:**
   ```bash
   git clone [TU_ENLACE_A_GITHUB]
   cd ClasificacionTerreno
   