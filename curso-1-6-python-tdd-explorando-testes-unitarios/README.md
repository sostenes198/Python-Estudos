# Links
* [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/)
* [https://pytest-cov.readthedocs.io/en/latest/](https://pytest-cov.readthedocs.io/en/latest/) 

# Comandos úteis

* `pipenv run pytest`
* `pipenv run pytest -v -m calcular_bonus`
* `pipenv run pytest --cov`
* `pipenv run pytest --cov=src tests`
* `pipenv run pytest --cov=src tests --cov-report term-missing`
* `pipenv run pytest --cov=src tests --cov-report html`

# 🧪 Ciclo de Vida do Pytest

Este documento explica como o **pytest** funciona por baixo dos panos, desde a inicialização até a execução e finalização dos testes.  
Saber esse ciclo ajuda a criar fixtures, entender onde hooks são executados e a padronizar a estratégia de testes.

---

## 📌 1. Configuração Inicial

1. Lê arquivos de configuração:
   - `pyproject.toml`
   - `pytest.ini`
   - `setup.cfg`
   - `tox.ini`
2. Carrega plugins instalados (ex.: `pytest-cov`, `pytest-mock`, `pytest-asyncio`).
3. Executa hooks de inicialização:
   - `pytest_configure`
   - `pytest_sessionstart`

---

## 📌 2. Descoberta de Testes

- Procura arquivos de teste (`test_*.py` ou `*_test.py`).
- Dentro de cada arquivo, coleta:
  - Funções `test_*`.
  - Métodos `test_*` dentro de classes `Test*`.
- Cria a **coleção de testes**.
- Executa hooks de coleta (`pytest_collectstart`, `pytest_collectreport`).

---

## 📌 3. Setup Global (Fixtures de Escopo)

- Inicializa fixtures de **escopo `session`**.
- Inicializa fixtures de **escopo `module`** para cada módulo de teste.
- Executa hook `pytest_runtest_setup`.

---

## 📌 4. Execução dos Testes

Para **cada teste**:

1. Resolve fixtures de escopo `function` ou `class`.
2. Executa `setup_function` / `setup_method` (se definidos).
3. Executa o corpo do teste.
4. Executa `teardown_function` / `teardown_method` (se definidos).
5. Libera fixtures do escopo `function`.
6. Executa hook `pytest_runtest_teardown`.

---

## 📌 5. Teardown Global

- Libera fixtures de escopo `module` e `session`.
- Executa hook `pytest_sessionfinish`.
- Gera relatórios (inclusive coverage, se habilitado).
- Retorna código de saída:
  - `0` → todos os testes passaram.
  - `1` → houve falhas.
  - Outros códigos indicam erros de uso ou interrupção.

---

## 🔄 Diagrama do Ciclo de Vida

```text
┌────────────────────┐
│ 1. Configuração    │
│ - Lê configs       │
│ - Carrega plugins  │
│ - Hooks init       │
└───────┬────────────┘
        │
┌───────▼────────────┐
│ 2. Coleta de Testes│
│ - Busca arquivos   │
│ - Coleta funções   │
│ - Cria coleção     │
└───────┬────────────┘
        │
┌───────▼────────────┐
│ 3. Setup Global    │
│ - Fixtures session │
│ - Fixtures module  │
└───────┬────────────┘
        │
┌───────▼────────────┐
│ 4. Execução Testes │
│ Para cada teste:   │
│  a) Fixtures func  │
│  b) Setup          │
│  c) Executa teste  │
│  d) Teardown       │
└───────┬────────────┘
        │
┌───────▼────────────┐
│ 5. Teardown Global │
│ - Libera fixtures  │
│ - Relatórios       │
│ - Código saída     │
└────────────────────┘
```

# 🧩 2. Entendendo Fixtures

Fixtures são funções que preparam o estado para os testes (setup) e podem opcionalmente fazer limpeza (teardown).
O pytest injeta automaticamente o valor retornado pela fixture nos testes que a solicitarem.

📌 Exemplo Básico
```python
import pytest

@pytest.fixture
def sample_data():
    return {"user": "alice", "age": 30}

def test_should_use_fixture(sample_data):
    assert sample_data["user"] == "alice"

```

🎯 Escopos das Fixtures

| Escopo              | Quando é criada                        | Quando é destruída           | Uso típico                                                       |
| ------------------- | -------------------------------------- | ---------------------------- | ---------------------------------------------------------------- |
| `function` (padrão) | Antes de **cada teste**                | Após o teste terminar        | Criar mocks, dados isolados, reset de estado                     |
| `class`             | Antes de todos os testes de uma classe | Depois que a classe termina  | Criar recursos caros mas reaproveitáveis dentro da mesma classe  |
| `module`            | Uma vez por arquivo de teste           | Quando o módulo termina      | Criar conexões, clientes HTTP, DB mocks                          |
| `session`           | Uma vez para **toda a execução**       | Ao final da sessão de testes | Configuração global, inicialização de banco fake, docker-compose |

📌 Exemplo com Escopos Diferentes
```python
import pytest

@pytest.fixture(scope="session")
def db_connection():
    print("🔗 Criando conexão global com o banco fake")
    yield "db-session"
    print("❌ Fechando conexão global")

@pytest.fixture(scope="module")
def module_data():
    print("📦 Criando dados para o módulo")
    return {"products": ["a", "b"]}

@pytest.fixture(scope="function")
def clean_state():
    print("🧹 Limpando estado antes do teste")
    return {"status": "fresh"}

def test_1(db_connection, module_data, clean_state):
    assert db_connection == "db-session"

def test_2(db_connection, module_data, clean_state):
    assert "a" in module_data["products"]

```
Quando você roda pytest -s, verá:

* db_connection é criado uma única vez na sessão.
* module_data é criado uma vez por módulo (arquivo de teste).
* clean_state é criado antes de cada teste.

# 📂 3. O Papel do conftest.py

O conftest.py é um arquivo especial para registrar fixtures reutilizáveis.
* Detectado automaticamente pelo pytest (não precisa importar manualmente).
* Pode estar em qualquer pasta (tests/, tests/api/, etc.).
* As fixtures nele são visíveis para todos os testes daquele diretório e subdiretórios.

📌 Exemplo de conftest.py
```python
# tests/conftest.py
import pytest
from myapp.db import create_test_db, drop_test_db

@pytest.fixture(scope="session")
def test_database():
    db = create_test_db()
    yield db
    drop_test_db(db)

@pytest.fixture(scope="function")
def mock_user():
    return {"id": 123, "name": "Alice"}
```

# ⚙️ 4. Configuração de addopts

Para padronizar as execuções, configure no seu pyproject.toml:
```toml
[tool.pytest.ini_options]
addopts = [
    "-ra",                # resumo dos testes xfails, xpasses, skips, etc.
    "--strict-markers",   # evita typos em markers
    "--cov=src",          # coverage da pasta src
    "--cov-report=term-missing",
    # "-m", "unit",       # <- descomente para rodar unit tests por padrão
]
```
Assim, ao rodar apenas pytest, essas opções serão aplicadas automaticamente.

É equivalente a rodar manualmente:

```bash
pytest -ra --strict-markers --cov=src --cov-report=term-missing
```

# 🏆 Boas Práticas

**Separe os testes por tipo:**

> tests/unit/, tests/integration/, tests/e2e/.

* **Use markers:**

```python
@pytest.mark.unit
@pytest.mark.integration
```


* **Isso permite rodar grupos de testes:**

```bash
pytest -m "unit"
pytest -m "integration"
```


* **Centralize fixtures no conftest.py para reaproveitamento e limpeza.**
* **Rode com --setup-show para visualizar a ordem de execução das fixtures:**

```bash
pytest -vv --setup-show
```


* **Ative coverage e relatórios para monitorar a qualidade dos testes.**

* **Use pytest-mock para criar e injetar mocks de forma mais legível.**