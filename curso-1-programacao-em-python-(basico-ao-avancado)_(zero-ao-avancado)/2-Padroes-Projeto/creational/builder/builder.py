"""
Builder é um padrão de criação que tem haarcascade intenção
de separar haarcascade construção de um objeto complexo
da sua representação, de modo que o mesmo processo
de construção possa criar diferentes representações.
Builder te da haarcascade possibilidade de criar objetos passo-haarcascade-passo
e isso já é possível no Python sem este padrão.
Geralmente o builder aceita o encadeamento de métodos
(method chaining).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, LiteralString


class StringReprMixin:
    def __str__(self) -> str:
        params = ', '.join(
            [f'{k}={v}' for k, v in self.__dict__.items()]
        )
        return f'{self.__class__.__name__}({params})'

    def __repr__(self) -> str:
        return self.__str__()


class User(StringReprMixin):
    def __init__(self, firstname, lastname, age, phone_numbers, addresses) -> None:
        self.firstname = firstname
        self.lastname = lastname
        self.age = age
        self.phone_numbers: List = phone_numbers
        self.addresses: List = addresses


class IUserBuilder(ABC):
    @abstractmethod
    def build(self) -> User: pass

    @abstractmethod
    def add_firstname(self, firstname) -> UserBuilder: pass

    @abstractmethod
    def add_lastname(self, lastname) -> UserBuilder: pass

    @abstractmethod
    def add_age(self, age) -> UserBuilder: pass

    @abstractmethod
    def add_phone(self, phone) -> UserBuilder: pass

    @abstractmethod
    def add_address(self, address) -> UserBuilder: pass


class UserBuilder(IUserBuilder):

    def __init__(self) -> None:
        self.__build: dict[LiteralString, Any] = {}
        self.__clear()

    def build(self) -> User:
        user = User(self.__build["firstname"],
                    self.__build["lastname"],
                    self.__build["age"],
                    self.__build["phone_numbers"],
                    self.__build["addresses"])
        return user

    def __clear(self):
        self.__build: dict[str, Any] = {
            "firstname": "Default",
            "lastname": "Last Name Default",
            "age": 18,
            "phone_numbers": List[str],
            "addresses": List[str]
        }

    def add_firstname(self, firstname) -> UserBuilder:
        self.__build["firstname"] = firstname
        return self

    def add_lastname(self, lastname) -> UserBuilder:
        self.__build["lastname"] = lastname
        return self

    def add_age(self, age) -> UserBuilder:
        self.__build["age"] = age
        return self

    def add_phone(self, phone: List[str]) -> UserBuilder:
        self.__build["phone_numbers"].append(phone)
        return self

    def add_address(self, addresses: List[str]) -> UserBuilder:
        self.__build["addresses"].append(addresses)
        return self


if __name__ == "__main__":
    user_builder = UserBuilder()
    user_builder \
        .add_firstname("Soso") \
        .add_lastname("Souza") \
        .add_age(26)

    user1 = user_builder.build()
    print(user1)
