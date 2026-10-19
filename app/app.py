import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf

# 1. Configuración de la página
st.set_page_config(page_title="Clasificador EuroSAT", page_icon="🌍", layout="centered")

# 2. Diccionario de clases exactas de EuroSAT
CLASES_EUROSAT = sorted([
    "AnnualCrop", "Forest", "HerbaceousVegetation", "Highway", 
    "Industrial", "Pasture", "PermanentCrop", "Residential", 
    "River", "SeaLake"
])

# 3. Carga del modelo con caché (para no recargar en cada interacción)
@st.cache_resource
def cargar_modelo():
    # Ajusta esta ruta a donde guardaste tu modelo final
    # Ejemplo asumiendo que corres app.py desde la raíz del proyecto
    ruta = "models/fine_tuned/modelo_efnetb0_ft_final.keras"
    return tf.keras.models.load_model(ruta)

try:
    modelo = cargar_modelo()
    modelo_cargado = True
except Exception as e:
    st.error(f"Error al cargar el modelo. Verifica la ruta: {e}")
    modelo_cargado = False

# 4. Interfaz Principal
st.title("🌍 Clasificador de Terreno - EuroSAT")
st.write("Sube una imagen satelital para predecir su tipo de cobertura terrestre utilizando una arquitectura EfficientNetB0 ajustada.")

# Cargador de archivos
archivo_subido = st.file_uploader("Elige una imagen satelital (JPG/PNG)...", type=["jpg", "png", "jpeg"])

if archivo_subido is not None and modelo_cargado:
    col_img, col_pred = st.columns(2)
    
    # Abrir y procesar la imagen original
    imagen_pil = Image.open(archivo_subido).convert("RGB")
    
    with col_img:
        st.image(imagen_pil, caption="Imagen Subida", use_container_width=True)
        
    with st.spinner('Procesando características...'):
        # 5. PREPROCESAMIENTO IDÉNTICO AL ENTRENAMIENTO
        # a. Redimensionar al "Campo Receptivo" de EfficientNet (128x128)
        imagen_redimensionada = imagen_pil.resize((128, 128))
        # b. Convertir a Array
        img_array = np.array(imagen_redimensionada)
        # c. Asegurar float32 (SIN dividir por 255, EfficientNet lo hace interno)
        img_array = img_array.astype('float32')
        # d. Añadir la dimensión de lote (Batch) -> Forma final: (1, 128, 128, 3)
        img_batch = np.expand_dims(img_array, axis=0)

        # 6. Predicción
        predicciones = modelo.predict(img_batch)[0]
        indice_predicho = np.argmax(predicciones)
        clase_predicha = CLASES_EUROSAT[indice_predicho]
        confianza_max = predicciones[indice_predicho]

    # 7. Despliegue de Resultados (Panel lateral derecho)
    with col_pred:
        st.subheader("Predicción:")
        st.write(f"### **{clase_predicha}**")
        st.write(f"Confianza: **{confianza_max*100:.2f}%**")

    # 8. Barra de probabilidades (Top 3) imitando el diagrama
    st.divider()
    st.write("#### Distribución de Probabilidades (Top 3)")
    
    # Obtener los 3 índices con mayores probabilidades
    top_3_indices = np.argsort(predicciones)[-3:][::-1]
    
    for i in top_3_indices:
        clase = CLASES_EUROSAT[i]
        prob = float(predicciones[i])
        
        # Columnas para alinear texto de clase y la barra de progreso
        col_texto, col_barra = st.columns([1, 3])
        with col_texto:
            st.write(f"**{clase}**")
        with col_barra:
            # Streamlit permite barras de progreso de 0.0 a 1.0
            st.progress(prob, text=f"{prob*100:.1f}%")