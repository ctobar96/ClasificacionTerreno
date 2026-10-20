import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
# IMPORTANTE: Importar el preprocesamiento específico de EfficientNet
from tensorflow.keras.applications.efficientnet import preprocess_input

# 1. Configuración de la página
st.set_page_config(page_title="Clasificador EuroSAT", page_icon="🌍", layout="centered")

# 2. Lista original en inglés (mantiene el orden exacto del entrenamiento)
CLASES_EUROSAT_EN = sorted([
    "AnnualCrop", "Forest", "HerbaceousVegetation", "Highway", 
    "Industrial", "Pasture", "PermanentCrop", "Residential", 
    "River", "SeaLake"
])

# 3. Diccionario de traducción al español 
TRADUCCION_CLASES = {
    "AnnualCrop": "Cultivo Anual",
    "Forest": "Bosque",
    "HerbaceousVegetation": "Vegetación Herbácea",
    "Highway": "Autopista / Carretera",
    "Industrial": "Zona Industrial",
    "Pasture": "Pastizal / Pasto",
    "PermanentCrop": "Cultivo Permanente",
    "Residential": "Zona Residencial",
    "River": "Río",
    "SeaLake": "Mar o Lago"
}

# 4. Carga del modelo con caché (para no recargar en cada interacción)
@st.cache_resource
def cargar_modelo():
    ruta = "models/fine_tuned/modelo_efnetb0_ft_final.keras"
    return tf.keras.models.load_model(ruta)

try:
    modelo = cargar_modelo()
    modelo_cargado = True
except Exception as e:
    st.error(f"Error al cargar el modelo. Verifica la ruta: {e}")
    modelo_cargado = False

# 5. Interfaz Principal
st.title("🌍 Clasificador de Terreno - EuroSAT")
st.write("Sube una imagen satelital para predecir su tipo de cobertura terrestre.")

# Cargador de archivos
archivo_subido = st.file_uploader("Elige una imagen satelital (JPG/PNG)...", type=["jpg", "png", "jpeg"])

if archivo_subido is not None and modelo_cargado:
    col_img, col_pred = st.columns(2)
    
    # Abrir y procesar la imagen original
    imagen_pil = Image.open(archivo_subido).convert("RGB")
    
    with col_img:
        st.image(imagen_pil, caption="Imagen Subida", use_container_width=True)
        
    with st.spinner('Procesando características...'):
        # 6. PREPROCESAMIENTO IDÉNTICO AL ENTRENAMIENTO
        # a. Redimensionar al "Campo Receptivo" de EfficientNet (128x128)
        imagen_redimensionada = imagen_pil.resize((128, 128))
        # b. Convertir a Array
        img_array = np.array(imagen_redimensionada)
        # c. Asegurar float32
        img_array = img_array.astype('float32')
        # d. Añadir la dimensión de lote (Batch) -> Forma final: (1, 128, 128, 3)
        img_batch = np.expand_dims(img_array, axis=0)
        # e. Aplicar la función de preprocesamiento oficial del modelo
        img_preprocesada = preprocess_input(img_batch)

        # 7. Predicción
        predicciones = modelo.predict(img_preprocesada)[0]
        indice_predicho = np.argmax(predicciones)
        
        # Obtener nombres en inglés y español
        clase_predicha_en = CLASES_EUROSAT_EN[indice_predicho]
        clase_predicha_es = TRADUCCION_CLASES[clase_predicha_en]
        confianza_max = predicciones[indice_predicho]

    # 8. Despliegue de Resultados (Panel lateral derecho)
    with col_pred:
        st.subheader("Predicción:")
        st.write(f"### **{clase_predicha_es}**")
        st.write(f"Confianza: **{confianza_max*100:.2f}%**")

    # 9. Barra de probabilidades (Top 3)
    st.divider()
    st.write("#### Distribución de Probabilidades (Top 3)")
    
    # Obtener los 3 índices con mayores probabilidades
    top_3_indices = np.argsort(predicciones)[-3:][::-1]
    
    for i in top_3_indices:
        clase_en = CLASES_EUROSAT_EN[i]
        clase_es = TRADUCCION_CLASES[clase_en] # Traducir al español de forma limpia
        prob = float(predicciones[i])
        
        # Columnas para alinear texto de clase y la barra de progreso
        col_texto, col_barra = st.columns([1.5, 3])
        with col_texto:
            st.write(f"**{clase_es}**")
        with col_barra:
            # Mostrar barra de progreso con el porcentaje respectivo
            st.progress(prob, text=f"{prob*100:.1f}%")