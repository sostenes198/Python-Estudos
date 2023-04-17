from typing import Callable, Any, List, Self, Type, Tuple, Dict, TypeVar
from functools import wraps
from inspect import signature


class LogDecorator(object):

    def __init__(self, method: object):
        self.method = method

    def __call__(self, *args, **kwargs):
        signature_method = signature(self.method)
        print(f'Executando metodo {self.method.__name__}: {signature_method} : {args}')
        result = self.method(*args, **kwargs)
        print(f'Resultado execução do metodo {self.method.__name__} : {result}')
        return result

        @classmethod
        def log_function(cls, func: Callable[[Type[Self], List[str], str], List[Self]]) -> Callable[[Type[Self], List[str], str], List[Self]]:
            @wraps(func)
            def internal(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Callable[[Type[Self], List[str], str], List[Self]]:
                return func

        return internal


T = TypeVar('T')


class MyReprDecorator:

    def __init__(self, msg: str):
        self.msg_ = msg
        
    def __call__(self, class_: T):
        
        def internal( *args, **kwargs):
            result = class_(*args, **kwargs)
            return result
        
        def define_repr(internal_self):
            class_name = internal_self.__class__.__name__
            class_dict = internal_self.__dict__
            return f'{self.msg_} {class_name}{class_dict}'
        
    
        class_.__repr__ = define_repr
        return internal


def adiciona_repr(cls):
    def meu_repr(self):
        class_name = self.__class__.__name__
        class_dict = self.__dict__
        return f'{class_name}{class_dict}'

    cls.__repr__ = meu_repr
    return cls
