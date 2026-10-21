# Usar una imagen oficial de python ligera
FROM python:3.11-slim

# Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de requerimientos al contenedor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el contenido del proyecto al contenedor
COPY . .

# Exponer el puerto el puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]