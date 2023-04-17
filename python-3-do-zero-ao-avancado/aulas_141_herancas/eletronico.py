from log import LogPrintMixin

class Eletronico:

    def __init__(self, nome: str) -> None:
        self._nome = nome
        self._ligado = False

    def ligar(self) -> None:
        if not self._ligado:
            self._ligado = True

    def desligar(self) -> None:
        if self._ligado:
            self._ligado = False


class SmarthPhone(Eletronico, LogPrintMixin):
    
    def ligar(self) -> None:
        super().ligar()
        
        if self._ligado:
            self.log_success(f'{self._nome} está ligado')
    
    def desligar(self) -> None:
        super().desligar()
        
        if not self._ligado:
            self.log_error(f'{self._nome} está desligado')