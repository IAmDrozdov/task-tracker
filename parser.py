import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    add_parser = subparsers.add_parser('add')
    add_parser.add_argument('-d', '--description', required=True)
    add_parser.add_argument('-dl', '--deadline')

    show_parser = subparsers.add_parser('show')
    show_parser.add_argument('id', nargs='?', action='store', type=int)

    remove_parser = subparsers.add_parser('remove')
    remove_parser.add_argument('id', type=int)
    return parser
