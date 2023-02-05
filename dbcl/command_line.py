from __future__ import unicode_literals

import sys
import os
import argparse

from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table
from sqlalchemy.exc import ResourceClosedError, NoSuchTableError

from pygments.lexers import SqlLexer

from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit.history import FileHistory
from terminaltables import SingleTable


_command_prefix = "--"


def prompt_for_url():
    url_from_env = os.getenv("DATABASE_URL", "")
    try:
        input_url = prompt("Connect to [%s]: " % url_from_env)
        if len(input_url) > 0:
            return input_url
        else:
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
    except Exception as e:
        print(e)
        sys.exit(1)


def print_data(data):
    print(SingleTable(data).table)


def print_result(result):
    try:
        print_data([result.keys()] + [row for row in result])
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
    except NoSuchTableError as e:
        print('No such table "%s"' % e)
        return

    data = [[m[0] for m in _column_info_mapping]]
    for col in table_info.columns:
        data.append([getattr(col, m[1]) for m in _column_info_mapping])

    print_data(data)


def process_command_info(info_args, connection, args):
    if len(info_args) > 1:
        print("usage: %sinfo [table_name]" % _command_prefix)
    elif len(info_args) == 0:
        print_data([["Database URL"]] + [[args.database_url]])

        metadata = MetaData(connection)
        metadata.reflect()
        print_data([["Tables"]] + sorted([[t] for t in metadata.tables.keys()]))
    else:
        _print_table_info(info_args[0], connection)


def process_command(cmd, connection, args):
    cmd_argv = cmd.split()
    if cmd_argv[0] == "%sinfo" % _command_prefix:
        process_command_info(cmd_argv[1:], connection, args)
    elif (
        cmd_argv[0] == "%sexit" % _command_prefix
        or cmd_argv[0] == "%squit" % _command_prefix
    ):
        sys.exit(0)
    else:
        print('Bad command "%s"' % cmd)


def prompt_for_command(args, connection, history):
    try:
        cmd = prompt("> ", lexer=PygmentsLexer(SqlLexer), history=history)
        if cmd.startswith(_command_prefix):
            process_command(cmd, connection, args)
        else:
            result = connection.execute(cmd)
            print_result(result)
    except KeyboardInterrupt:
        return
    except EOFError:
        sys.exit(0)
    except Exception as e:
        print(e)
        return


def command_loop():
    args = get_args(sys.argv[1:])
    try:
        connection = get_engine(args).connect()
    except Exception as e:
        print(e)
        sys.exit(1)
    history = FileHistory(os.path.expanduser("~/.dbcl_history"))

    while True:
        prompt_for_command(args, connection, history)
