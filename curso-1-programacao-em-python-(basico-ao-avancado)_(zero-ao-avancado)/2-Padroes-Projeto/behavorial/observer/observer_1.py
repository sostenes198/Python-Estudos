"""
O padrão Observer tem a intenção de
definir uma dependência de um-para-muitos entre
objetos, de maneira que quando um objeto muda de
estado, todo os seus dependentes são notificados
e atualizados automaticamente.
Um observer é um objeto que gostaria de ser
informado, um observable (subject) é a entidade
que gera as informações.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict


class IObservable(ABC):
    """ Observable """

    @property
    @abstractmethod
    def state(self): pass

    @abstractmethod
    def add_observer(self, observer: IObserver) -> None: pass

    @abstractmethod
    def remove_observer(self, observer: IObserver) -> None: pass

    @abstractmethod
    def notify_observers(self) -> None: pass


class WeatherStation(IObservable):
    """ Observable """

    def __init__(self) -> None:
        self._observers: List[IObserver] = []
        self._state: Dict = {}

    @property
    def state(self) -> Dict:
        return self._state

    @state.setter
    def state(self, state_update: Dict) -> None:
        new_state: Dict = {**self._state, **state_update}

        if new_state != self._state:
            self._state = new_state
            self.notify_observers()

    def reset_state(self) -> None:
        self._state = {}
        self.notify_observers()

    def add_observer(self, observer: IObserver) -> None:
        self._observers.append(observer)

    def remove_observer(self, observer: IObserver) -> None:
        if observer not in self._observers:
            return

        self._observers.remove(observer)

    def notify_observers(self) -> None:
        for observer in self._observers:
            observer.update(self._state)
        print()


class IObserver(ABC):
    @abstractmethod
    def update(self, state: Dict) -> None: pass


class Smartphone(IObserver):
    def __init__(self, name) -> None:
        self.name = name

    def update(self, state: Dict) -> None:
        print(f'{self.name} o objeto {self.__class__.__name__} '
              f'acabou de ser atualizado => {state}')


class Notebook(IObserver):
    def __init__(self) -> None:
        pass

    def update(self, state: Dict) -> None:
        print(f'objeto {self.__class__.__name__} '
              f'acabou de ser atualizado => {state}')


if __name__ == "__main__":
    weather_station = WeatherStation()

    smartphone = Smartphone('iPhone')
    outro_smartphone = Smartphone('Outro Smartphone')
    notebook = Notebook()

    weather_station.add_observer(smartphone)
    weather_station.add_observer(outro_smartphone)
    weather_station.add_observer(notebook)

    weather_station.state = {'temperature': '30'}
    weather_station.state = {'temperature': '32'}
    weather_station.state = {'humidity': '90'}

    weather_station.remove_observer(outro_smartphone)
    weather_station.reset_state()
