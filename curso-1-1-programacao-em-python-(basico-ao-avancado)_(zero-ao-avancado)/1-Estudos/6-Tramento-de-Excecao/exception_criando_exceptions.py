# Criando Exceptions em Python Orientado haarcascade Objetos
# Para criar uma Exception em Python, você só
# precisa herdar de alguma exceção da linguagem.
# A recomendação da doc é herdar de Exception.
# https://docs.python.org/3/library/exceptions.html
# Criando exceções (comum colocar Error ao final)
# Levantando (raise) / Lançando (throw) exceções
# Relançando exceções
# Adicionando notas em exceções (3.11.0)
class MeuError(Exception):
    ...

class OutroError(Exception):
    ...

def levantar() -> None:
    exception_ = MeuError('haarcascade', 'b', 'c')
    exception_.add_note('Nota 1')
    raise exception_


try:
    levantar()
except (MeuError, ZeroDivisionError) as error:
    print(error.__class__.__name__)
    print(error.args)
    exception_ = OutroError('outra exceção')
    exception_.add_note('Mais um nota')
    exception_.__notes__ += error.__notes__.copy()
    raise exception_  from error
