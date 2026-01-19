# Estudos 

## Gerenciamento de pacotes

### Pip

Tutorial instalando pip para gerenciamento de pacotes pyhton: [installing-packages](https://packaging.python.org/pt_BR/latest/tutorials/installing-packages/)

**Comandos básicos:**

* Certifique-se que pip, setuptools e wheel estejam atualizados:

    ```
    py -m pip install --upgrade pip setuptools wheel
    ```

* Listar todos os pacotes instalados
        
    ```
    pip list --outdated
    ```

#### Atualizando dependências globais do PIP:

[https://www.activestate.com/resources/quick-reads/how-to-update-all-python-packages/](https://www.activestate.com/resources/quick-reads/how-to-update-all-python-packages/)

**Powershell:**

    pip freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}
    
**Bash:**

    pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3 install -U

### Pipenv

Tutorial para instalação do pipenv: [Tutorial de instalação](https://packaging.python.org/pt_BR/latest/tutorials/managing-dependencies/)

Local onde os ambientes virtual são criados: C:\Users\{CURRENT_USER}\.virtualenvs

Links uteis:

1) [pipenv](https://pipenv.pypa.io/en/latest/)

2) [advanced](https://docs.pipenv.org/advanced/)

#### ☤ Configuração com variáveis de ambiente¶

`PIPENV_VENV_IN_PROJECT` Se definido, use `.venv` no seu diretório de projeto em vez do gerenciador global de virtualenv pew.


**Comandos básicos:**

* pipenv para listar comandos:
        
    ```
    pipenv
    ```

*  criar ambiente virtual

    ```
    pipenv --python 3.11.1 (3.11.1<VERSION_PYTON>)
    ``` 

* remove a virtualenv created by "pipenv run"
  
    ```
    pipenv --rm
    ```

* Listar local onde o ambiente virtual está

    ```
    pipenv --venv
    ```

* Locais ondes envs são criados

  ```
  %USERPROFILE%\.virtualenvs
  ```

## Mypy:

### Documentação:
[https://mypy.readthedocs.io/en/stable/getting_started.html](https://mypy.readthedocs.io/en/stable/getting_started.html)

### Instalação:
     pipenv install mypy --save-dev

### Comandos:
    
#### Executar análise em um arquivo:
    mypy {FILE_NAME}.py


## Pipx
[https://pipx.pypa.io/stable/](https://pipx.pypa.io/stable/)

Para gerenciar executaveis python. <br>
Instalando pipx no python global: <br>
`pip install pipx` <br>
`pipx ensurepath`

Apos instaladado o `pipx`, no windows é necessário executar o comando: 
`pipx ensurepath` para adicionar os executaveis do pipx ao ambiente para ser executado
pela linha de comando.

### Comandos:

`pipx list` -> Lista pacotes instalados

`pipx install {PACKAGE_NAME}` -> Instala pacote

`pipx uninstall {PACKAGE_NAME}` -> Remove pacote

`pipx upgrade {PACKAGE_NAME}` -> Atualiza pacote

# Poetry

> Local onde os ambientes virtuais criados para o `poetry` <br>
> estão: `%USERPROFILE%/AppData\Local\pypoetry\Cache\virtualenvs` <br>


### Comandos:

`poetry config --list` -> Lista todas as configurações do poetry

`poetry env info --path` -> Exibe path de onde o `env` encontra-se 

`poetry env list` -> Lista todos os enviroments gerenciados

`poetry env remove {{POETRY_ENV_NAME}}` -> Remove enviroment selecionado

`poetry env use {{PYTHON_VERSION}}` ->  Activates or creates a new virtualenv for the current project.

`poetry new {{PROJECT_NAME}}` -> Cria novo projeto com gerenciador poetry

`poetry init` -> Inicializa projeto com gerenciador poetry

`poetry config virtualenvs.in-project true` -> Se quise configurar para o poetry criar env no mesmo diretorio do projeto

`poetry cache clear pypi --all` -> Limpar cache de arquivos baixados (Isso libera muito espaço)

`%LocalAppData%\pypoetry\Cache` -> Local onde os pacotes e caches do poetry são instalados


## Gerenciador de múltiplas versões python
[https://github.com/pyenv-win/pyenv-win](https://github.com/pyenv-win/pyenv-win)

![pyenv_usage.png](imgs/pyenv_usage.png)

---

## Limpando dependências Pipenv Poetry venv

### 1. Limpando o POETRY

O Poetry, por padrão, cria todos os ambientes em uma pasta centralizada e oculta, o que faz a gente esquecer que eles existem.

**Opção A: Remover um ambiente específico (Se você estiver na pasta do projeto)**

```bash
# Lista os ambientes associados a este projeto
poetry env list

# Remove o ambiente
poetry env remove <nome-do-ambiente-que-apareceu-na-lista>

```

**Opção B: O "Expurgo" Geral (Recomendado para liberar espaço)**
Como o Poetry centraliza tudo, você pode ir lá e apagar a pasta inteira. Na próxima vez que rodar `poetry install` em um projeto, ele recria apenas o necessário.

* **No Linux/Mac:**
A pasta fica em: `~/.cache/pypoetry/virtualenvs`
Comando para limpar tudo:
```bash
rm -rf ~/.cache/pypoetry/virtualenvs/*

```


* **No Windows:**
A pasta geralmente fica em: `%LOCALAPPDATA%\pypoetry\virtualenvs`
(Caminho exato costuma ser `C:\Users\SEU_USUARIO\AppData\Local\pypoetry\virtualenvs`).
*Vá até lá pelo Explorador de Arquivos e delete as pastas.*

---

### 2. Limpando o PIPENV

O Pipenv também centraliza os ambientes, dificultando o rastreio.

**Opção A: Remover o ambiente atual**
Entre na pasta do projeto e rode:

```bash
pipenv --rm

```

**Opção B: Apagar tudo manualmente**
O Pipenv costuma guardar tudo em `~/.local/share/virtualenvs` (Linux/Mac) ou `C:\Users\SEU_USUARIO\.virtualenvs` (Windows).

* **Comando de limpeza (Linux/Mac):**
```bash
rm -rf ~/.local/share/virtualenvs/*

```

* **No Windows:** Delete o conteúdo da pasta `.virtualenvs` no seu usuário.

---

### 3. Limpando VIRTUALENV / VENV (Padrão)

Diferente dos anteriores, o `venv` e o `virtualenv` geralmente criam uma pasta (chamada `.venv`, `venv` ou `env`) **dentro** do diretório do seu projeto.

Para limpar, você deve deletar a pasta manualmente.

**Dica Ninja**
Se você tem muitos projetos espalhados e quer encontrar todas as pastas `venv` para decidir qual apagar, use este comando. Ele procura pastas chamadas `.venv` ou `venv` e mostra o tamanho delas:

**Linux**:
```bash
# Procura a partir da sua pasta home (pode demorar um pouco)
find ~ -type d \( -name ".venv" -o -name "venv" \) -prune -exec du -sh {} +

```

**Windows:**

Passo 1: Apenas encontrar (Listar) Este comando vai varrer sua pasta de usuário (C:\Users\SeuNome) procurando 
por pastas chamadas .venv ou venv e listar o caminho delas.

```powershell
Get-ChildItem -Path $env:USERPROFILE -Recurse -Directory -Include ".venv","venv" -ErrorAction SilentlyContinue | Select-Object FullName
```

* Nota: Pode demorar alguns minutos dependendo de quantos arquivos você tem. O ErrorAction SilentlyContinue serve para ignorar 
pastas de sistema onde você não tem permissão, evitando erros vermelhos na tela.

* Se quiser apagar, basta dar um `rm -rf` na pasta(s) identificada.*

---

### 4. Bônus: Limpando o Cache do PIP

Além dos ambientes, o próprio gerenciador de pacotes (`pip`) guarda cópias de downloads (`.whl`) para instalar mais rápido depois. Isso ocupa muito espaço.

Para limpar o cache geral do Python:

```bash
# Funciona no Linux, Mac e Windows
pip cache purge
```

*Isso geralmente libera instantaneamente de 500MB a 2GB.*

---

### Resumo da Faxina

1. Rode `pip cache purge`.
2. Vá na pasta de cache do Poetry e delete tudo.
3. Vá na pasta de cache do Pipenv e delete tudo.
4. Rode `poetry install` apenas no projeto que você está trabalhando **agora**.
