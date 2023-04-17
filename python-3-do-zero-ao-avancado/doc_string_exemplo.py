""" Documetação do meu modulo

    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit 
    in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, 
    sunt in culpa qui officia deserunt mollit anim id est laborum."
"""

from typing import Optional

variavael_1 = 10


def soma(x: int, y: int) -> int:
    """Soma X e Y
    
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit 
        in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, 
        sunt in culpa qui officia deserunt mollit anim id est laborum."
        
        :param x: Numero 1
        :type x: int or float
        :param y: Numero 2
        :type y: int or float
        
        :return: A soma entre x e y
        :rtype: int or float
    """
    
    
def multiplica(x: int, y: int, z: Optional[int] = None) -> int:
    """ Multiplica x, y e/ou z
    
    Multiplica x e y. Se z for enviado, multiplica x, y e z.
    
    :param x: int
    :param y: int
    :param z: Optional[int] default is None
    :return: Retorna a multiplicação de x e y e/ou x, y e z.
    :rtype: int
    """
    
    if z is None:
        return x * y
    return x * y * z
    
    
variavael_2 = 20
variavael_3 = 30
variavael_4 = 40