from __future__ import unicode_literals

import argparse
import os
import sys

from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import prompt
from pygments.lexers.sql import SqlLexer
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.exc import NoSuchTableError, ResourceClosedError
from terminaltables import SingleTable

COMMAND_PREFIX = "--"


def prompt_for_url():
    url_from_env = os.getenv("DATABASE_URL", "")
    try:
        input_url = prompt(f"Connect to [{url_from_env}]: ")
        if len(input_url) > 0:
            return input_url

        return url_from_env

    except KeyboardInterrupt:
        sys.exit(1)
    except EOFError:
        sys.exit(0)


def get_args(arguments):
    # TODO add more details usage info
    parser = argparse.ArgumentParser(description="Connect to a database.")
    parser.add_argument(
        "database_url",
        metavar="URL",
        type=str,
        nargs="?",
        default="",
        help="the database URL to connect to",
    )

    args = parser.parse_args(arguments)

    while len(args.database_url) == 0:
        args.database_url = prompt_for_url()

    return args


def get_engine(args):
    try:
        return create_engine(args.database_url)
    except Exception as exc:
        print(exc)
        sys.exit(1)


def print_data(data):
    print(SingleTable(data).table)


def print_result(result):
    try:
        print_data([result.keys()] + list(result))
    except ResourceClosedError:
        pass


_column_info_mapping = (
    ("Column", "key"),
    ("Type", "type"),
    ("Primary Key", "primary_key"),
    ("Index", "index"),
    ("Default", "default"),
    ("Allow NULL", "nullable"),
)


def _print_table_info(table, connection):
    try:
        table_info = Table(table, MetaData(connection), autoload=True)
    except NoSuchTableError as exc:
        print(f'No such table "{exc}"')
        return

    data = [[m[0] for m in _column_info_mapping]]
    for col in table_info.columns:
        data.append([getattr(col, m[1]) for m in _column_info_mapping])

    print_data(data)


def process_command_info(info_args, connection, args):
    if len(info_args) > 1:
        print(f"usage: {COMMAND_PREFIX}info [table_name]")
    elif len(info_args) == 0:
        print_data([["Database URL"]] + [[args.database_url]])

        metadata = MetaData(connection)
        metadata.reflect()
        print_data([["Tables"]] + sorted([[t] for t in metadata.tables.keys()]))
    else:
        _print_table_info(info_args[0], connection)


def process_command(cmd, connection, args):
    cmd_argv = cmd.split()
    if cmd_argv[0] == f"{COMMAND_PREFIX}info":
        process_command_info(cmd_argv[1:], connection, args)
    elif (
        cmd_argv[0] == f"{COMMAND_PREFIX}exit" or cmd_argv[0] == f"{COMMAND_PREFIX}quit"
    ):
        sys.exit(0)
    else:
        print(f'Bad command "{cmd}"')


def prompt_for_command(args, connection, history):
    try:
        cmd = prompt("> ", lexer=PygmentsLexer(SqlLexer), history=history)
        if cmd.startswith(COMMAND_PREFIX):
            process_command(cmd, connection, args)
        else:
            result = connection.execute(cmd)
            print_result(result)
    except KeyboardInterrupt:
        return
    except EOFError:
        sys.exit(0)
    except Exception as exc:
        print(exc)
        return


def command_loop():
    args = get_args(sys.argv[1:])
    try:
        connection = get_engine(args).connect()
    except Exception as exc:
        print(exc)
        sys.exit(1)
    history = FileHistory(os.path.expanduser("~/.dbcl_history"))

    while True:
        prompt_for_command(args, connection, history)
