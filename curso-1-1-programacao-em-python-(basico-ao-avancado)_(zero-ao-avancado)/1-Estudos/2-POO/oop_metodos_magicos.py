"""
2-POO - Métodos Mágicos

Métodos Mágicos, são todos os métodos que utilizam dunder.

# dunder init -> __init__()
def __init__(self, titulo, autor, paginas):
    self.titulo = titulo
    self.autor = autor
    self.paginas = paginas

Dunder > Double Underscore

# dunder repr -> Representação do objeto
def __repr__(self):
    return f'{self.titulo} escrito por {self.autor}'
"""
import \
    inspect
from inspect import signature

class Livro(object):

    def __init__(self, titulo, autor, paginas):
        self.titulo = titulo
        self.autor = autor
        self.paginas = paginas

    def __str__(self):
        return self.titulo

    # def __repr__(self):
    #     return f'{self.titulo} escrito por {self.autor}'

    def __len__(self):
        return self.paginas

    def __del__(self):
        print('Um objeto do tipo Livro foi deletado da memória')

    def __add__(self, outro):
        return f'{self} - {outro}'

    def __mul__(self, outro):
        if isinstance(outro, int):
            msg = ''
            for n in range(outro):
                msg += ' ' + str(self)
            return msg
        return 'Não posso multiplicar'
    
    def __setattr__(self, key, value):    
        constructor_parameters: list = list(signature(self.__init__).parameters.keys())
        if key in constructor_parameters:
            print("Contém atributo")
            super().__setattr__(key, value)
        else:
            raise Exception("Não suportado propriedades dinâmicas")
        pass
    

livro1 = Livro('Python Rocks!', 'Geek University', 400)
# livro2 = Livro('Inteligência Artificial com Python', 'Geek University', 350)

livro1.new_property = 10

# 
# print(livro1)
# 
# print(livro2)
# 
# print(len(livro1))
# print(len(livro2))
# 
# print(livro1 + livro2)
# 
# print(livro1 * 5)
