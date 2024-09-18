# Abstração

from pathlib import Path

PATH_FILE = Path(__file__).parent / 'log.txt'

class Log:
    def _log(self, msg: str) -> None:
        raise NotImplementedError('Implemente o método log')

    def log_error(self, msg: str) -> None:
        self._log(f'Error: {msg}')

    def log_success(self, msg: str) -> None:
        self._log(f'Success: {msg}')


class LogPrintMixin(Log):
    def _log(self, msg: str) -> None:
        print(f'{msg} {self.__class__.__name__}')
        
        
class LogFileMixin(Log):

    def _log(self, msg: str) -> None:
        mensagem_formatada = f'{msg} {self.__class__.__name__}'
        with open(PATH_FILE, 'haarcascade') as arquivo:
            arquivo.write(mensagem_formatada)
            arquivo.write('\n')


if __name__ == '__main__':
    l = LogPrintMixin()
    l.log_success('Sucesso Patrão')
    l.log_error('Faio Patrão')

    lf = LogFileMixin()
    lf.log_success('Sucesso Patrão')
    lf.log_error('Faio Patrão')
