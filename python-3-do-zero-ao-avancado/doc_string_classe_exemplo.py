""" Documetação do modulo

    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit 
    in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, 
    sunt in culpa qui officia deserunt mollit anim id est laborum."
"""

from typing import Optional


class Foo:
    """ Documetação da classe

        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
    
    """   
    
    def soma(self, x: int, y: int) -> int:
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
        return x + y


    def multiplica(self, x: int, y: int, z: Optional[int] = None) -> int:
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
        
    def bar(self):    
        """ Oque esse método faz ...
        
        :raise: NotImplementedError: Se o método não for definido
        
        :return: None
        :rtype: None
        """
        raise NotImplementedError('Test')
    