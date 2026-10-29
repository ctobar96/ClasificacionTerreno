Para llevar la arquitectura de tu **Clasificador EuroSAT en Google Cloud Run** al nivel estándar de la industria usando Infrastructure as Code (IaC), lo recomendable es estructurar tu código de Terraform de forma modular y configurar un **almacenamiento remoto del estado (GCS Backend)** para evitar desincronizaciones en WSL2 o GitHub Actions.

---

### 1. Estructura recomendada de archivos

Crea una carpeta `terraform/` en la raíz de tu proyecto para mantener la infraestructura separada del código de Python:

```text
ClasificacionTerreno/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── models/
│   └── fine_tuned/
│       └── modelo_efnetb0_ft_final.keras
├── app.py
├── Dockerfile
├── requirements.txt
└── terraform/
    ├── provider.tf      # Configuración del proveedor de GCP y Backend
    ├── main.tf          # Recursos principales (APIs, IAM, Cloud Run)
    ├── variables.tf     # Declaración de variables
    ├── terraform.tfvars # Valores reales de las variables
    └── outputs.tf       # Salidas (URLs, cuentas de servicio)

```

---

### 2. Archivos de Terraform listos para usar

#### `terraform/provider.tf`

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Estado remoto en Google Cloud Storage (opcional pero muy recomendado)
  # backend "gcs" {
  #   bucket = "tf-state-clasificacion-terreno-eurosat"
  #   prefix = "terraform/state"
  # }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

```

#### `terraform/variables.tf`

```hcl
variable "gcp_project_id" {
  type        = string
  description = "ID del proyecto en Google Cloud"
  default     = "clasificacion-terreno-eurosat"
}

variable "gcp_region" {
  type        = string
  description = "Región predeterminada para los recursos"
  default     = "us-central1"
}

variable "service_name" {
  type        = string
  description = "Nombre del servicio de Cloud Run"
  default     = "clasificador-eurosat"
}

```

#### `terraform/main.tf`

```hcl
# 1. Activar APIs de Google Cloud necesarias
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# 2. Cuenta de Servicio dedicada a GitHub Actions
resource "google_service_account" "github_deployer" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions Deployer"
  depends_on   = [google_project_service.apis]
}

# 3. Roles IAM necesarios para el despliegue automático
resource "google_project_iam_member" "deployer_roles" {
  for_each = toset([
    "roles/run.admin",
    "roles/cloudbuild.builds.editor",
    "roles/iam.serviceAccountUser",
    "roles/storage.admin",
    "roles/artifactregistry.admin"
  ])
  project = var.gcp_project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

# 4. Servicio Google Cloud Run (Configuración v2)
resource "google_cloud_run_v2_service" "app" {
  name     = var.service_name
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    session_affinity = true

    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/cloud-run-source-deploy/${var.service_name}:latest"

      ports {
        container_port = 8501
      }

      resources {
        limits = {
          cpu    = "1000m" # 1 CPU
          memory = "2Gi"   # 2 GB RAM para Keras/EfficientNet
        }
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# 5. Permitir invocación pública sin autenticación
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = google_cloud_run_v2_service.app.project
  location = google_cloud_run_v2_service.app.location
  name     = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

```

#### `terraform/outputs.tf`

```hcl
output "cloud_run_url" {
  value       = google_cloud_run_v2_service.app.uri
  description = "URL pública del clasificador en Cloud Run"
}

output "service_account_email" {
  value       = google_service_account.github_deployer.email
  description = "Email de la cuenta de servicio creada para CI/CD"
}

```

---

### 3. Flujo de ejecución en WSL2

Para aplicar la infraestructura desde tu terminal local:

```bash
# 1. Instalar Terraform en Ubuntu / WSL2 (si aún no lo tienes)
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install terraform

# 2. Entrar a la carpeta de Terraform e inicializar
cd terraform/
terraform init

# 3. Previsualizar los cambios
terraform plan

# 4. Crear la infraestructura completa en Google Cloud
terraform apply

```

---

### 4. Buenas prácticas para mantener en `.gitignore`

Asegúrate de no subir los archivos de estado local de Terraform a Git agregando esto a tu `.gitignore`:

```text
# Terraform
.terraform/
*.tfstate
*.tfstate.backup
*.tfvars
!terraform.tfvars.example

```