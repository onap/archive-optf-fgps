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
#!/usr/bin/env python2.7


import argparse
import json
import os.path
import sys
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valet.bootstrapper import Bootstrapper
from valet.solver.ostro import Ostro
from valet.utils.logger import Logger


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Logging', add_help=False)  # <<<2
    parser.add_argument('config', help='config file path (required)')
    parser.add_argument('-db', metavar='keyspace_string', help='override keyspace with typed in value')
    parser.add_argument('-stdout', action='store_true', help='also print debugging log to stdout')
    parser.add_argument("-?", "--help", action="help", help="show this help message and exit")
    opts = parser.parse_args()

    # Prepare configuration and logging.
    # noinspection PyBroadException
    try:
        config_file_d = open(opts.config, 'r')
        config_file = config_file_d.read()
        config = json.loads(config_file)
        config_file_d.close()

        logger_config = config.get("logging")

        if not os.path.exists(logger_config.get("path")):
            os.makedirs(logger_config.get("path"))

        # create all loggers and save an instance of the debug logger
        logger = Logger(logger_config, console=opts.stdout).get_logger('debug')
    except Exception:
        print("error while configuring: " + traceback.format_exc())
        sys.exit(2)

    try:
        config_file_dir = os.path.dirname(opts.config)
        version_file_name = config_file_dir + "/version.json"
        version_file_d = open(version_file_name, 'r')
        version_json = json.dumps(json.loads(version_file_d.read()))
        logger.info("Starting Valet with version: " + version_json)
        version_file_d.close()
    except Exception:
        logger.warning("Warning! Error while printing version: " + traceback.format_exc())


    # Boostrap all components and configure them.
    # noinspection PyBroadException
    try:
        if opts.db:
            config['db']['keyspace'] = opts.db

        bootstrapper = Bootstrapper(config, logger)
        if not bootstrapper.config_valet():
            print("error while configurating")
    except Exception:
        print("error while bootstrapping: " + traceback.format_exc())
        sys.exit(2)

    # Start valet-engine (aka. Ostro).
    ostro = Ostro(bootstrapper)
    ostro.run_ostro()
