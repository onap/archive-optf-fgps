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


import argparse
import json
import os
import sys

import lib.tables as tables
from lib.song import Song

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from valet.engine.db_connect.db_handler import DBHandler
from valet.engine.db_connect.locks import Locks, later
from valet.utils.logger import Logger


def options():
    parser = argparse.ArgumentParser(description='\033[34mManual Locking And Unlocking Of Valet Regions.\033[0m', add_help=False)
    Song.add_args(parser)

    g1 = parser.add_argument_group('Control Music Locks')
    ex = g1.add_mutually_exclusive_group()
    ex.add_argument('-unlock', metavar="region", help='unlock this region')
    ex.add_argument('-lock', metavar="region", help='lock this region')

    g2 = parser.add_argument_group('Update Locks In Region Table')
    ex = g2.add_mutually_exclusive_group()
    ex.add_argument('-delete', metavar="region", help='delete region from table')
    ex.add_argument('-add', metavar="region", help='update/add region to table')
    g2.add_argument('-timeout', metavar="seconds", help='seconds till region expires (for -add)')

    group = parser.add_argument_group("Change The Output")
    group.add_argument("-?", "--help", action="help", help="show this help message and exit")
    group.add_argument('-show', action='store_true', help='print out regions (locking) table')

    return parser.parse_args()


# MAIN
if __name__ == "__main__":
    opts = options()

    logger = Logger().get_logger('console')
    config = json.loads(open(opts.config).read())
    music_config = config.get("music")
    music_config["keyspace"] = config.get("db")["keyspace"]
    music = Song(opts, config, logger)
    dbh = DBHandler(music, config.get("db"), logger)

    if opts.add:
        timeout = opts.timeout if opts.timeout else config["engine"]["timeout"]
        dbh.add_region(opts.add, later(seconds=int(timeout)))
        logger.debug("added region to table")

    if opts.lock:
        if Locks(dbh, 0).got_lock(opts.lock) == "ok":
            logger.debug("added region lock")
        else:
            logger.debug("failed to add region lock")

    if opts.unlock:
        Locks.unlock(dbh, opts.unlock)
        logger.debug("deleted region lock '%s'" % opts.unlock)

    if opts.delete:
        dbh.delete_region(opts.delete)
        logger.debug("deleted region from table")

    if opts.show:
        music.keyspace = dbh.keyspace
        tables.Regions(music, logger).read(names=True)

    sys.exit(0)
