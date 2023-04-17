# Estudos 

## Gerenciamento de pacotes

### Pip

Tutorial instalando pip para gerenciamento de pacotes pyhton: [installing-packages](https://packaging.python.org/pt_BR/latest/tutorials/installing-packages/)

**Comandos básicos:**

* Certifique-se que pip, setuptools e wheel estejam atualizados:
        
        py -m pip install --upgrade pip setuptools wheel

### Pipenv

Tutorial para instalação do pipenv: [Tutorial de instalação](https://packaging.python.org/pt_BR/latest/tutorials/managing-dependencies/)

Local onde os ambientes virtual são criados: C:\Users\{CURRENT_USER}\.virtualenvs

Links uteis:

1) [pipenv](https://pipenv.pypa.io/en/latest/)


**Comandos básicos:**

* pipenv para listar comandos:
        
        pipenv

*  criar ambiente virtual

        pipenv --python 3.11.1 (3.11.1<VERSION_PYTON>) 

* remove a virtualenv created by "pipenv run"
  
        pipenv --rm

* Listar local onde o ambiente virtual está

        pipenv --venv

## Mypy:

### Documentação:
    https://mypy.readthedocs.io/en/stable/getting_started.html

### Instalação:
     pipenv install mypy --save-dev

### Comandos:
    
#### Executar análise em um arquivo:
    mypy {FILE_NAME}.py

