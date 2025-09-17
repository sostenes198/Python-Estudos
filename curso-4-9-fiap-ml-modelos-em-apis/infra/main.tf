terraform {
  required_providers {
    vercel = {
      source  = "vercel/vercel"
      version = "~> 1.9"
    }
  }
}

provider "vercel" {

}

variable "build_dir" {
  type    = string
  default = "../"
}

resource "vercel_project" "fastapi" {
  name      = "fastapi-curso-4"
  framework = "fastapi"
}

resource "vercel_project_environment_variable" "jwt_secret" {
  project_id = vercel_project.fastapi.id
  key        = "JWT_SECRET"
  value      = "MY_SECRET_HERE"
  target     = ["production", "preview", "development"]
}

resource "vercel_project_environment_variable" "disable_db" {
  project_id = vercel_project.fastapi.id
  key        = "DISABLE_DB"
  value      = "1"
  target     = ["production", "preview", "development"]
}

# 👉 agora apontamos para a SAÍDA do build (não para ../)
data "vercel_project_directory" "build" {
  path = var.build_dir
}

resource "vercel_deployment" "deploy" {
  project_id  = vercel_project.fastapi.id
  files       = data.vercel_project_directory.build.files
  path_prefix = data.vercel_project_directory.build.path
  production  = true
}
