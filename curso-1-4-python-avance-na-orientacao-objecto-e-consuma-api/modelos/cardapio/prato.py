from modelos.cardapio.item_cardapio import ItemCardapio


class Prato(ItemCardapio):
    def __init__(self, nome, preco, descricao):
        super().__init__(nome, preco)
        self._descricao = descricao

    def aplicar_desconto(self):
        self._preco -= (self._preco * 0.08)

    def exibir_descricao_cardapio(self):
        return f'{self}. Nome:{self._nome} Preco: {self._preco} Descrição: {self._descricao}'
