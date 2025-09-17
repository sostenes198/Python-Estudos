# Fast Api modelos de ML + Vercel

# Estrutura do projeto
.
├─ main.py                     # app FastAPI
├─ modelo_iris.pkl
├─ predictions.db              # usado apenas localmente (não persiste na Vercel)
├─ pyproject.toml / poetry.lock
├─ requirements.txt            # gerado do poetry para a Vercel ler
├─ vercel.json                 # runtime/roteamento
└─ infra/
   └─ main.tf                  # Terraform: projeto, env vars e (opcional) deploy

# Dependencias extras do poetry necessárias

`poetry self add poetry-plugin-export`

# Comandos a serem executados

1. `poetry run pip list --format=freeze > requirements.txt` || `poetry export -f requirements.txt -o requirements.txt --without-hashes`

# Subir vercel no terraform

```bash
vercel login

# vincula o diretório ao projeto (use o mesmo nome do resource Terraform)
vercel link --project fastapi-curso-4 --yes

vercel pull --environment=production
```
 
```bash
vercel build --prod
```

```bash
rm -rf vercel_output

cp -R .vercel/output vercel_output
```

```bash
export VERCEL_API_TOKEN=seu_token

cd infra

terraform init
terraform apply
```

```bash
terraform destroy
```