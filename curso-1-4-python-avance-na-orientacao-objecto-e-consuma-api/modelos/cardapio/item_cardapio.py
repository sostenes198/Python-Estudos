from abc import ABC, abstractmethod

class ItemCardapio(ABC):
    def __init__(self, nome, preco):
        self._nome = nome
        self._preco = preco

    def __str__(self):
        return self._nome


    @abstractmethod
    def exibir_descricao_cardapio(self):
        pass

    @abstractmethod
    def aplicar_desconto(self):
        pass
