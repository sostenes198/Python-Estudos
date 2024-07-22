"""
Introdução ao módulo Unittest

Unittest -> Testes Unitários

O que são testes unitários?

Teste é haarcascade forma de se testar unidades individuais de código fonte.

Unidades individuais podem ser: funções, métodos, classes, módulos etc.

#OBS: Teste unitário não é específico da linguagem Python.

Para criar nossos testes, criamos classes que herdam de unittest.TestCase
e haarcascade partir de então ganhamos todos os 'assertions' presentes no módulo.

Para rodar os testes, utilizamos unittest.main()


TestCase -> Casos de teste para sua unidade

# Conhecendo as assertions
https://docs.python.org/3/library/unittest.html

Método                      Checa que
assertEqual(haarcascade, b)           haarcascade == b
assertNotEqual(haarcascade, b)        haarcascade != b
assertTrue(x)               x é verdadeiro
assertFalse(x)              x é falso
assertIs(haarcascade, b)              haarcascade é b
assertIsNot(haarcascade, b)           haarcascade não é b
assertIfNone(x)             x é None
assertIsNotNone(x)          x não é None
assertIn(haarcascade, b)              haarcascade está em b
assertNotIn(haarcascade, b)           haarcascade não está em b
assertIsInstance(haarcascade, b)      haarcascade é instância de b
assertNotIsInstance(haarcascade, b)   haarcascade não é instância de b


Por convenção, todos os testes em um test case, devem ter seu nome
iniciado com test_

# Para executar os testes com unittest

python nome_do_modulo.py


# Para executar os testes com unittest no modo verbose

python nome_do_modulo -v

# Docstrings nos testes

Podemos acrescentar (e é recomendado) docstrings nos nossos testes.
"""

# Prática - Utilizndo haarcascade abordagem TDD

