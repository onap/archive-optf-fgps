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


import json
import os
import sys
import time
from datetime import datetime
from textwrap import TextWrapper

import pytz


class Tables(object):
    """parent class for all tables."""

    schema = None
    alias = None

    def __init__(self, music, logger):
        """Initializer. Accepts target host list, port, and path."""

        self.music = music
        self.logger = logger
        self.key = None
        self.keyspace = music.keyspace
        self.tz = pytz.timezone('America/New_York')

    @classmethod
    def table_alias(cls):
        s = cls.__name__
        s = s[0].lower() + s[1:]
        return [s] + cls.alias

    @staticmethod
    def option_choices():
        choices = []
        aliases = None
        for table in Tables.__subclasses__():
            choices = choices + table.table_alias()
            for alias in choices:
                if aliases:
                    aliases = aliases + ' ' + alias
                else:
                    aliases = alias

        choices.append('all')

        return {
            "alias":  TextWrapper(subsequent_indent="    ", initial_indent="    ", width=79).fill(aliases),
            "choices": choices
        }

    def table(self):
        """Return tables name (same as class name but all lc)."""

        s = type(self).__name__
        return s[0].lower() + s[1:]

    def utc2local(self, utc):
        """Change utc time to local time for readability."""

        return " (" + datetime.fromtimestamp(utc, self.tz).strftime('%Y-%m-%d %I:%M:%S %Z%z') + ")"

    def get_rows(self, ids=None, raw=False):
        """ get_rows read table, or rows by id and return rows array """

        # TODO if ids == None and hasattr(self, 'ids'): ids = self.ids
        key = None if (ids is None) else self.key
        rows = []

        for row_id in ids or [None]:
            if raw:
                rows.append(json.dumps(self.music.read_row(self.keyspace, self.table(), key, row_id), sort_keys=True, indent=4))
                continue

            result = self.music.read_row(self.keyspace, self.table(), key, row_id)["result"]

            # strip "Row n"
            for _, data in sorted(result.iteritems()):
                rows.append(data)

        if raw:
            return rows

        if len(rows) == 1:
            rows = rows[0]  # one row? not a list

        return rows

    def read(self, ids=None, json_file=None, raw=False, rows=None, names=None):
        """ read rows (array or single dict) to stdout or to a file """

        if rows is None:
            rows = self.get_rows(ids, raw)

        if raw:
            if names:
                print "\n" + self.table()
            for row in rows:
                print row
            return

        if isinstance(rows, list):
            for row in rows:
                if not ("timestamp" in row or "expire_time" in row):
                    break
                for key in (["timestamp", "expire_time"]):
                    if (not (key in row)) or (row[key] is None):
                        continue
                    try:
                        row[key] = row[key] + self.utc2local(float(row[key])/1000)
                    except ValueError:
                        row[key] = "Error: "+ row[key]
                        
        else:
            row = rows
            for key in (["timestamp", "expire_time"]):
                if (not (key in row)) or (row[key] is None):
                    continue
                try:
                    row[key] = row[key] + self.utc2local(float(row[key])/1000)
                except ValueError:
                    row[key] = "Error: "+ row[key]

        if json_file is None:
            if names:
                print "\n" + self.table()
            print json.dumps(rows, sort_keys=True, indent=4)
            return

        fh = open(json_file, "w")
        fh.write(json.dumps(rows, sort_keys=True, indent=4))
        fh.close() 

    def create(self, json_file=None):
        """ add records from a file to db """

        if json_file and os.path.exists(json_file):
                inf = open(json_file)
                f = json_file
        else:
                inf = sys.stdin
                f = "stdin"

        self.logger.info("Create " + self.table() + " from: " + f)
        self.insert(json.loads(inf.read()))

    def insert(self, data):
        """ add records """

        self.logger.debug(data)

        if isinstance(data, list):
            for row in data:
                if "timestamp" in row:
                    row['timestamp'] = int(round(time.time() * 1000))
                self.music.create_row(self.keyspace, self.table(), row) 
        else:
            row = data
            if "timestamp" in row:
                row['timestamp'] = int(round(time.time() * 1000))
            self.music.create_row(self.keyspace, self.table(), row)

    def create_table(self):
        """ create table """

        self.logger.info(self.schema)
        self.music.create_table(self.keyspace, self.table(), self.schema)

    def update(self, json_file):
        """Update a row. Not atomic."""
        
        self.logger.info("Update " + self.table() + " from: " + json_file)
        data = json.loads(open(json_file).read())
        self.logger.debug(data)

        if isinstance(data, list):
            for row in data:
                self.music.update_row_eventually(self.keyspace, self.table(), row)
        else:
            self.music.update_row_eventually(self.keyspace, self.table(), data)

    def delete(self, ids):
        """ delete records db based on id """

        for row_id in ids:
            self.logger.info("Delete from" + self.table() + " id: " + row_id)
            self.music.delete_row_eventually(self.keyspace, self.table(), self.key, row_id)

    def clean_table(self):
        """ delete all records in table """

        ids = []
        rows = self.get_rows()

        if isinstance(rows, list):
            for row in rows:
                ids.append(row[self.key])
        else:
            row = rows
            ids.append(row[self.key])

        for row_id in ids:
            self.music.delete_row_eventually(self.keyspace, self.table(), self.key, row_id)

#  Subclasses of Tables:


class Requests(Tables):
    alias = ["req", "q"]
    key = "request_id"
    schema = json.loads('{ "request_id": "text", "timestamp": "text", "request": "text", "PRIMARY KEY": "(request_id)" }')

    def __init__(self, music, logger):
        Tables.__init__(self, music, logger)
        self.key = Requests.key


class Results(Tables):
    alias = ["resu", "u"]
    key = "request_id"
    schema = json.loads('{ "request_id": "text", "status": "text", "timestamp": "text", "result": "text", "PRIMARY KEY": "(request_id)" }')

    def __init__(self, music, logger):
        Tables.__init__(self, music, logger)
        self.key = Results.key

class Group_rules(Tables):
    alias = ["rule", "gr"]
    key = "id"
    schema = json.loads('{ "id": "text", "app_scope": "text", "type": "text", "level": "text", "members": "text", "description": "text", "groups": "text", "status": "text", "timestamp": "text", "PRIMARY KEY": "(id)" }')

    def __init__(self, music, logger):
        Tables.__init__(self, music, logger)
        self.key = Group_rules.key


class Stacks(Tables):
    alias = ["stack", "s"]
    key = "id"
    schema = json.loads('{ "id": "text", "last_status": "text", "datacenter": "text", "stack_name": "text", "uuid": "text", "tenant_id": "text", "metadata": "text", "servers": "text", "prior_servers": "text", "state": "text", "prior_State": "text", "timestamp": "text", "PRIMARY KEY": "(id)" }')

    def __init__(self, music, logger):
        Tables.__init__(self, music, logger)
        self.key = Stacks.key


class Stack_id_map(Tables):
    alias = ["map", "m"]
    key = "request_id"
    schema = json.loads('{ "request_id": "text", "stack_id": "text", "timestamp": "text", "PRIMARY KEY": "(request_id)" }')

    def __init__(self, music, logger):
        Tables.__init__(self, music, logger)
        self.key = Stack_id_map.key


class Resources(Tables):
    alias = ["reso", "o"]
    key = "id"
    schema = json.loads('{ "id": "text", "url": "text", "resource": "text", "timestamp": "text", "requests": "text", "PRIMARY KEY": "(id)" }')

    def __init__(self, music, logger):
        Tables.__init__(self, music, logger)
        self.key = Resources.key


class Regions(Tables):
    alias = ["reg", "i", "lock"]
    key = "region_id"
    schema = json.loads('{ "region_id ": "text", "timestamp": "text", "last_updated ": "text", "keystone_url": "text", "locked_by": "text", "locked_time ": "text", "expire_time": "text", "PRIMARY KEY": "(region_id)" }')

    def __init__(self, music, logger):
        Tables.__init__(self, music, logger)
        self.key = Regions.key


class Groups(Tables):
    alias = ["group", "g"]
    key = "id"
    schema = json.loads('{ "id ": "text", "uuid": "text", "type ": "text", "level": "text", "factory": "text", "rule_id ": "text", "metadata ": "text", "server_list": "text", "member_hosts": "text", "status": "text", "PRIMARY KEY": "(id)" }')

    def __init__(self, music, logger):
        Tables.__init__(self, music, logger)
        self.key = Groups.key


if __name__ == "__main__":

    print Tables.option_choices()
