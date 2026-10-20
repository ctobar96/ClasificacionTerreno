
import mlflow

# Crear o seleccionar un experimento
mlflow.set_experiment("ClasificacionTerreno")

# Registrar una ejecución de prueba
with mlflow.start_run(run_name="prueba_inicial"):

    mlflow.log_param("modelo", "CNN")
    mlflow.log_param("tamano_imagen", "64x64")
    mlflow.log_param("canales", 3)

    # Métrica ficticia solo para comprobar el registro
    mlflow.log_metric("accuracy_prueba", 0.85)

    print("Experimento registrado correctamente.")

