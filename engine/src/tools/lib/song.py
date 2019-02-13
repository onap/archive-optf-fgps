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
"""Song is music for scripts

    This is a subclass of music that scripts can use to add an option to override:
        add_args - the commandline arguments that Song uses
        keyspace - to allow the same script to run vs other databases
        hosts table - to allow the same script to run vs other databases on other machines
        connect - login may be different for other databases
"""


import argparse
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # ../../..
from valet.utils.logger import Logger
from valet.engine.db_connect.db_apis.music import Music


def hosts(opts, config):
    """override configs hosts"""

    hosts_json = os.path.join(sys.path[-1], "tools", "lib", "hosts.json")
    _hosts = json.loads(open(hosts_json).read())
    config["music"]["hosts"] = _hosts["music"][opts.env or "dev"]["hosts"]["a"]

    if opts.verbose:
        print "hosts: " + str(config["music"]["hosts"])


# noinspection PyBroadException
class Song(Music):
    """music but with script helpers"""

    Keyspaces = {
        "cw":  "valet_TestDB123",
        "cmw": "valet_cmw",
        "pk":  "valet_TestDB420",
        "pk2": "valetdb2",
        "pn":  "pn2",
        "st":  "valet_saisree",
        "ist": "valet_IST",
        "gj":  "valet_TestDB2"
    }
    Keyspaces.update(dict((v, v) for k, v in Keyspaces.iteritems()))  # full name is valid too

    def __init__(self, opts, config, logger):
        if opts.env:
            hosts(opts, config)

        self.keyspace = config["db"]["keyspace"]
        self.defaultKeyspace = True 

        if opts.Keyspace:
            if opts.Keyspace == "all":
                self.keyspace = opts.Keyspace
            else:
                self.keyspace = Song.Keyspaces[opts.Keyspace]
            self.defaultKeyspace = False

        if opts.db:
            self.keyspace = opts.db
            self.defaultKeyspace = False
       
        # TODO cmw: move keyspace into music object, pass in like config["keyspace"] = self.keyspace

        super(Song, self).__init__(config, logger)

    @staticmethod
    def add_args(parser):
        """add common parser arguments"""
        default_config = "/opt/config/solver.json"
        if not os.path.isfile(default_config):
            default_config = os.path.join(sys.path[-1], "config", "solver.json")

        valid_keyspaces = Song.Keyspaces.keys()
        valid_keyspaces.append("all")
        valid_keyspaces_str = "{" + ",".join(valid_keyspaces) + "}"

        valid_hosts = ["a1", "a2", "a3", "b3", "ab", "m"]
        valid_env = ["dev", "ist", "e2e"]

        song_args = parser.add_argument_group("Common Music Arguments")
        song_args.add_argument('-env', metavar=valid_env, help='pick set of hosts -deprecated', choices=valid_env)
        song_args.add_argument('-host', metavar=valid_hosts, help='pick set of hosts -deprecated', choices=valid_hosts)
        ex = song_args.add_mutually_exclusive_group()
        ex.add_argument('-Keyspace', metavar=valid_keyspaces_str, help='override configs keyspace with a users', choices=valid_keyspaces)
        ex.add_argument('-db', metavar='keyspace_string', help='override keyspace with typed in value')
        song_args.add_argument('-config', metavar='file', default=default_config, help="default: " + default_config)
        song_args.add_argument('-verbose', action='store_true', help="verbose output")

    def create_keyspace(self, keyspace):
        """override creates a keyspace."""

        data = {
            'replicationInfo': {
                "DC2": 3,
                "DC1": 3,
                "class": "NetworkTopologyStrategy"
            },
            'durabilityOfWrites': True,
            'consistencyInfo': {
                'type': 'eventual',
            },
        }

        path = '/keyspaces/%s' % keyspace
        try:
            self.rest.request(method='post', path=path, data=data)
            return 0
        except Exception:
            # "this exception should be handled here but it's done in music :("
            return -1


def main():
    parser = argparse.ArgumentParser(description='Extended Music DB.', add_help=False)
    Song.add_args(parser)
    parser.add_argument("-?", "--help", action="help", help="show this help message and exit")
    opts = parser.parse_args()

    logger = Logger().get_logger('console')

    config = json.loads(open(opts.config).read())
    music = Song(opts, config, logger)

    print json.dumps(config.get("music"))
    print (music.keyspace)


# MAIN
if __name__ == "__main__":
    main()
    sys.exit(0)
