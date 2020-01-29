#
# -------------------------------------------------------------------------
#   Copyright (c) 2019 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#
#!/usr/bin/env python3

"""
Commandline Rest Interface Music  (CRIM)
For help invoke with crim.py --help
"""


import argparse
import json
import os
from pprint import pprint
import re
import sys
import traceback

from lib.song import Song
from lib.tables import Tables

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # ../../..
from valet.utils.logger import Logger


# options <<<1
def options():
    toc = Tables.option_choices()

    parser = argparse.ArgumentParser(description='\033[34mCommandline Rest-Interface to Music.\033[0m', add_help=False)
    Song.add_args(parser)

    group = parser.add_argument_group("Choose table\n\033[48;5;227m" + toc["alias"] + "\033[0m")

    group.add_argument('-action', help='perform insert, update, delete, delete all, create table', choices=['i', 'u', 'd', 'D', 'c'])
    group.add_argument('-id',  metavar='ID', action="append", help='id(s) in a table; (multiples allowed)')
    group.add_argument('-file', help='json file required for -action create')
    group.add_argument('-table', metavar='table', help='perform action on this table', default="request", choices=toc["choices"])

    group = parser.add_argument_group("Add/Delete Schema")
    group.add_argument("-sA", "-schemaAdd", metavar='keyspace', dest="schemaAdd", help="create keyspace")
    group.add_argument("-sD", "-schemaDel", metavar='keyspace', dest="schemaDel", help="delete keyspace")

    group = parser.add_argument_group("Query Tables")
    group.add_argument('-read', metavar='all|table', action='append', help='read all or tables (multiples allowed)', choices=toc["choices"])
    group.add_argument('-names', action='store_true', help='show names of tables on read')
    group.add_argument('-Raw', action='store_true', help='dont strip out the music added fields')

    group = parser.add_argument_group("Other Output")
    group.add_argument("-?", "--help", action="help", help="show this help message and exit")
    group.add_argument("-json", metavar='FILE', help="view json file")
    group.add_argument('-show', action='store_true', help='show db stuff')
    group.add_argument('-ShowConfig', action='store_true', help='show config stuff')
    group.add_argument('-vt', '-viewTables', action='store_true', dest="viewTables", help='list tables (hardcoded)')
    group.add_argument('-vs', '-viewSchema', action='store_true', dest="viewSchema", help='list table schema (hardcoded)')

    return parser.parse_args()  # >>>1


# setTable <<<1
def _set_table(opts_table):
    """ set table based on requested table. """

    for sub_table in Tables.__subclasses__():
        if opts_table in sub_table.table_alias():
            return sub_table(music, logger)
# >>>1


question = lambda q: raw_input(q).lower().strip()[0] == "y"


def clean_env(var):
    if var in os.environ:
        del os.environ[var]


""" MAIN """
if __name__ == "__main__":
    clean_env('HTTP_PROXY')
    clean_env('http_proxy')
    opts = options()

    # Get logger; Read config and strike up a song <<<1
    logger = Logger().get_logger('console')
    config = json.loads(open(opts.config).read())
    music = Song(opts, config, logger)
    # >>>1

    if opts.viewTables:
        for table in Tables.__subclasses__():
            print((re.sub("[[\]',]", '', str(table.table_alias()))).split(" ")[0])
        sys.exit(0)

    if opts.viewSchema:
        for table in Tables.__subclasses__():
            sys.stdout.write(re.sub("[[\]',]", '', str(table.table_alias())) + ' ')
            print(json.dumps(table.schema, sort_keys=True, indent=2), "\n")
        sys.exit(0)

    """ Keyspace Create """  # <<<1
    if opts.schemaAdd:
        sys.exit(music.create_keyspace(opts.schemaAdd))

    """ Keyspace Delete """  # <<<1
    if opts.schemaDel:
        if question("You sure you wanna delete keyspace '%s'? [y/n] " % opts.schemaDel):
            sys.exit(music.drop_keyspace(opts.schemaDel))

    # all the tables listed with '-read's <<<1
    if opts.read:
        if 'all' in opts.read:
            if music.keyspace == "all":
                sys.exit("read all tables for all keyspaces is not currently supported")

            for table in Tables.__subclasses__():
                table(music, logger).read(raw=opts.Raw, names=True)
            sys.exit(0)

        if music.keyspace == "all":
            opts.names = True
            for keyspace in Song.Keyspaces.keys():
                music.keyspace = Song.Keyspaces[keyspace]
                print("\n-----------------    %s : %s    -----------------" % (keyspace, music.keyspace))
                # noinspection PyBroadException
                try:
                    for tName in opts.read:
                        _set_table(tName).read(ids=opts.id, json_file=opts.file, names=opts.names, raw=opts.Raw)
                except Exception as e:
                    pass
            sys.exit(0)

        for tName in opts.read:
            _set_table(tName).read(ids=opts.id, json_file=opts.file, names=opts.names, raw=opts.Raw)
        sys.exit(0)

    table = _set_table(opts.table)

    # show all db stuff <<<1
    if opts.show or opts.ShowConfig:
        if opts.show:
            print("music")
            pprint(music.__dict__, indent=2)
            print("\nrest")
            pprint(music.rest.__dict__, indent=2)

            if table is not None:
                print("\n", table.table())
                pprint(table.__dict__, indent=2)

        if opts.ShowConfig:
            print (json.dumps(config, indent=4))

        sys.exit(0)
    # >>>1

    """ VIEW JSON FILE open, convert to json, convert to string and print it """  # <<<1
    if opts.json:
        # noinspection PyBroadException
        try:
            print (json.dumps(json.loads(open(opts.json).read()), indent=4))
        except Exception as e:
            print (traceback.format_exc())
            sys.exit(2)
        sys.exit(0)

    """ Insert use json file to add record to database """  # <<<1
    if opts.action == 'i':
        table.create(opts.file)
        sys.exit(0)
    
    """ CREATE Table """  # <<<1
    if opts.action == 'c':
        table.create_table()
        sys.exit(0)
    
    """ UPDATE use json file to update db record """  # <<<1
    if opts.action == 'u':
        if not opts.file or not os.path.exists(opts.file):
            print("--file filename (filename exists) is required for update")
            sys.exit(1)

        table.update(opts.file)
        sys.exit(0)
    
    """ DELETE  use id to delete record from db -- requres ID """  # <<<1
    if opts.action == 'd':
        if not opts.id:
            print("--id ID is required for delete")
            sys.exit(1)

        if opts.id:
            table.delete(opts.id)
            sys.exit(0)

    """ DELETE ALL from table"""  # <<<1
    if opts.action == 'D':
        table.clean_table()
        sys.exit(0)
# >>>1
