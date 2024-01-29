"""
Na programação 2-POO, o termo factories (fábrica) refere-se a uma classe ou método
que é responsável por criar objetos.
Vantagens:
    Permitem criar um sistema com baixo acoplamento entre classes porque
    ocultam as classes que criam os objetos do código cliente.
    Facilitam a adição de novas classes ao código, porque o cliente não
    conhece e nem utiliza a implementação da classe (utiliza a factories).
    Podem facilitar o processo de "cache" ou criação de "singletons" porque a
    fábrica pode retornar um objeto já criado para o cliente, ao invés de criar
    novos objetos sempre que o cliente precisar.
Desvantagens:
    Podem introduzir muitas classes no código
Vamos ver 2 tipos de Factory da GoF: Factory method e Abstract Factory
Nessa aula:
Simple Factory <- Uma espécie de Factory Method parametrizado
Simple Factory pode não ser considerado um padrão de projeto por si só
Simple Factory pode quebrar princípios do SOLID
"""
from abc import ABC, abstractmethod


class Veiculo(ABC):
    @abstractmethod
    def buscar_cliente(self) -> None: pass


class CarroLuxo(Veiculo):
    def buscar_cliente(self) -> None:
        print('Carro de luxo está buscando o cliente...')


class CarroPopular(Veiculo):
    def buscar_cliente(self) -> None:
        print('Carro popular está buscando o cliente...')


class MotoLuxo(Veiculo):
    def buscar_cliente(self) -> None:
        print('Moto de luxo está buscando o cliente...')


class MotoPopular(Veiculo):
    def buscar_cliente(self) -> None:
        print('Moto popular está buscando o cliente...')


class VeiculoFactory(ABC):
    def __init__(self, tipo) -> None:
        self._carro = self.get_carro(tipo)

    @staticmethod
    @abstractmethod
    def get_carro(tipo: str) -> Veiculo:
        pass


class ZonaNorteVeiculosFactory(VeiculoFactory):
    @staticmethod
    def get_carro(tipo: str) -> Veiculo:
        if tipo == 'luxo':
            return CarroLuxo()
        if tipo == 'popular':
            return CarroPopular()
        if tipo == 'moto':
            return MotoPopular()
        if tipo == 'moto_luxo':
            return MotoLuxo()
        assert 0, 'Veículo não existe'


class ZonaSulVeiculosFactory(VeiculoFactory):

    @staticmethod
    def get_carro(tipo: str) -> Veiculo:
        if tipo == 'popular':
            return CarroPopular()
        assert 0, 'Veiculo não existe'
        

if __name__ == "__main__":
    from random import choice


    veiculos_disponiveis_zona_norte = ['luxo', 'popular', 'moto', 'moto_luxo']
    veiculos_disponiveis_zona_sul = ['popular']

    for i in range(10):
        carro = ZonaNorteVeiculosFactory.get_carro(choice(veiculos_disponiveis_zona_norte))
        carro.buscar_cliente()
        
    print()

    for i in range(10):
        carro2 = ZonaSulVeiculosFactory.get_carro(choice(veiculos_disponiveis_zona_sul))
        carro2.buscar_cliente()
