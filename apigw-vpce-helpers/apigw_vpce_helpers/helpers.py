import os


def get_env(name):
    try:
        return os.environ[name]
    except KeyError:
        WIDTH = os.get_terminal_size().columns
        print('*' * WIDTH)
        print()
        print(f'Set the environment variable named "{name}" and try again.'.center(WIDTH))
        print()
        print('*' * WIDTH)
        print()
        raise SystemExit(f'Missing environment variable: {name}.')