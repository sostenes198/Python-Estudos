from modelos.cardapio.item_cardapio import ItemCardapio


class Bebida(ItemCardapio):
    def __init__(self, nome, preco, tamanho):
        super().__init__(nome, preco)
        self._tamanho = tamanho

    def aplicar_desconto(self):
        self._preco -= (self._preco * 0.05)

    def exibir_descricao_cardapio(self):
        return f'{self}. Nome:{self._nome} Preco: {self._preco} Tamanho: {self._tamanho}'
