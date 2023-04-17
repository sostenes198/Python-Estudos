def execute_command(commaad: str) -> None:
    print('')
    print('commannd 1')
    match commaad:
        case 'ls':
            print('Listing files')
        case 'cd':
            print('Changing directory')
        case _:
            print('Command not implemented')

    print('rest of the code')


def execute_command2(commaad: str) -> None:
    print('')
    print('commannd 2')
    match commaad.split():
        case ['ls' | 'list', path, *_] | ['listing', path, *_]:
            print('Listing files ', path)
        case ['cd', *directories] if len(directories) <= 1:
            for directory in directories:
                print('Changing directory ', directory)
        case _:
            print('Command not implemented')

    print(commaad.split())


execute_command2('ls c/user --force')
execute_command2('cd c/soso')


def execute_command3(command: dict) -> None:
    print('')
    print('commannd 3')
    match command:
        case {'command': 'ls', 'directories': [_, *_]}:
            print("Deu MATCH")
            for directory in command['directories']:
                print('Changing directory ', directory)
        case _:
            print('Command not implemented')


execute_command3({'command': 'ls', 'directories': ['/users', '/home']})

from dataclasses import dataclass


@dataclass
class Command:
    command: str
    directories: list[str]


def execute_command4(command: Command) -> None:
    print('')
    print('commannd 4')
    match command:
        case Command(command='ls', directories=[_, *_]):
            print("Deu MATCH")
            for directory in command.directories:
                print('Changing directory ', directory)
        case _:
            print('Command not implemented')


execute_command4(Command('ls', ['users', 'home']))