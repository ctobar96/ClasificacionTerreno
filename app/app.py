import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import matplotlib.pyplot as plt
# IMPORTANTE: Importar el preprocesamiento específico de EfficientNet
from tensorflow.keras.applications.efficientnet import preprocess_input


# 1. Configuración de la página
st.set_page_config(page_title="Clasificador EuroSAT", page_icon="🌍", layout="wide") # Usamos 'wide' para aprovechar mejor el espacio con el sidebar

@st.cache_resource
def cargar_modelo():
    return tf.keras.models.load_model("modelo_eurosat.keras")

modelo = cargar_modelo()

# 2. Lista original en inglés
CLASES_EUROSAT_EN = sorted([
    "AnnualCrop", "Forest", "HerbaceousVegetation", "Highway", 
    "Industrial", "Pasture", "PermanentCrop", "Residential", 
    "River", "SeaLake"
])

# 3. Diccionario de traducción al español sin emojis (Limpio y Profesional)
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

# 4. Función para generar el gráfico de radar
def generar_grafico_radar(predicciones, clases_en, traduccion):
    top_5_indices = np.argsort(predicciones)[-5:]
    valores = [predicciones[i] for i in top_5_indices]
    categorias = [traduccion[clases_en[i]] for i in top_5_indices]
    
    valores = np.concatenate((valores, [valores[0]]))
    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += angulos[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True)) # Ajustado el tamaño para el sidebar
    
    ax.plot(angulos, valores, color='#1f77b4', linewidth=2, linestyle='solid')
    ax.fill(angulos, valores, color='#1f77b4', alpha=0.25)
    
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angulos[:-1]), categorias, fontsize=8, fontweight='semibold')
    
    ax.set_rlabel_position(0)
    plt.yticks([0.25, 0.50, 0.75, 1.0], ["25%", "50%", "75%", "100%"], color="grey", size=7)
    plt.ylim(0, 1.05)
    
    plt.tight_layout()
    return fig

# 5. Carga del modelo con caché
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

# --- PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("### **Información del Proyecto**")
    st.write("🌍 *Clasificador de Terreno - EuroSAT*")
    st.caption("Análisis de Cobertura Terrestre mediante Deep Learning")
    st.divider()

# --- INTERFAZ PRINCIPAL ---
st.title("🌍 Clasificador de Terreno - EuroSAT")
st.write("Sube una imagen satelital para predecir su tipo de cobertura terrestre utilizando una arquitectura EfficientNetB0 ajustada.")

# Cargador de archivos
archivo_subido = st.file_uploader("Elige una imagen satelital (JPG/PNG)...", type=["jpg", "png", "jpeg"])

if archivo_subido is not None and modelo_cargado:
    col_img, col_pred = st.columns(2)
    
    imagen_pil = Image.open(archivo_subido).convert("RGB")
    
    with col_img:
        st.image(imagen_pil, caption="Imagen Subida", use_container_width=True)
        
    with st.spinner('Procesando características...'):
        # Preprocesamiento
        imagen_redimensionada = imagen_pil.resize((128, 128))
        img_array = np.array(imagen_redimensionada)
        img_array = img_array.astype('float32')
        img_batch = np.expand_dims(img_array, axis=0)
        img_preprocesada = preprocess_input(img_batch)

        # Predicción
        predicciones = modelo.predict(img_preprocesada)[0]
        indice_predicho = np.argmax(predicciones)
        
        clase_predicha_en = CLASES_EUROSAT_EN[indice_predicho]
        clase_predicha_es = TRADUCCION_CLASES[clase_predicha_en]
        confianza_max = predicciones[indice_predicho]

    # Mostrar el resultado principal al lado de la imagen
    with col_pred:
        st.subheader("Predicción Principal:")
        st.write(f"## **{clase_predicha_es}**")
        st.write(f"Confianza: **{confianza_max*100:.2f}%**")
        
        st.divider()
        st.write("#### Top 3 Clases Más Probables")
        top_3_indices = np.argsort(predicciones)[-3:][::-1]
        for i in top_3_indices:
            clase_en = CLASES_EUROSAT_EN[i]
            clase_es = TRADUCCION_CLASES[clase_en]
            prob = float(predicciones[i])
            
            st.write(f"**{clase_es}** ({prob*100:.1f}%)")
            st.progress(prob)

    # --- INTEGRACIÓN DEL GRÁFICO DE RADAR EN EL PANEL LATERAL ---
    with st.sidebar:
        st.markdown("### **Análisis de Probabilidad**")
        # Generar el gráfico de radar
        fig_radar = generar_grafico_radar(predicciones, CLASES_EUROSAT_EN, TRADUCCION_CLASES)
        # Renderizarlo en el sidebar
        st.pyplot(fig_radar)
# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.divider()

f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    st.markdown("#### **Desarrollado por:**")
    st.write("👨‍💻 **Cristian Tobar Morales**")
    st.caption("Magíster en Data Science")

with f_col2:
    st.markdown("#### **Proyecto:**")
    st.write("🌍 *Clasificador de Terreno - EuroSAT*")
    st.caption("Análisis de Cobertura Terrestre")

with f_col3:
    st.markdown("#### **Información:**")
    st.write("🚀 **Versión:** 1.1.1")
    st.caption("Última actualización: Octubre 2026")

st.markdown(
    """
    <div style='text-align: center; color: grey; padding-top: 20px;'>
        <p>© 2026 <b>Cristian Tobar Morales</b>. <br> 
         Todos los derechos reservados. | Esta aplicación es de uso estrictamente profesional y privado.</p>
    </div>
    """, 
     unsafe_allow_html=True
)