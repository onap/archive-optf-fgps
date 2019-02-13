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
import copy


class MemDB(object):

    def __init__(self, _config, _logger):
        self.logger = _logger

        self.keyspace = _config.get("keyspace")
        self.requests_table = _config.get("requests_table")
        self.results_table = _config.get("results_table")
        self.group_rules_table = _config.get("group_rules_table")
        self.groups_table = _config.get("groups_table")
        self.stacks_table = _config.get("stacks_table")
        self.resources_table = _config.get("resources_table")
        self.stack_id_map_table = _config.get("stack_id_map_table")

        self.requests = {}
        self.results = {}
        self.group_rules = {}
        self.groups = {}
        self.stacks = {}
        self.resources = {}
        self.stack_id_map = {}

    def read_all_rows(self, keyspace, table):
        rows = {"result": {}}

        if table == self.requests_table:
            for k, v in self.requests.iteritems():
                rows["result"][k] = copy.deepcopy(v)
        elif table == self.results_table:
            for k, v in self.results.iteritems():
                rows["result"][k] = copy.deepcopy(v)
        elif table == self.group_rules_table:
            for k, v in self.group_rules.iteritems():
                rows["result"][k] = copy.deepcopy(v)
        elif table == self.groups_table:
            for k, v in self.groups.iteritems():
                rows["result"][k] = copy.deepcopy(v)

        return rows

    def insert_atom(self, keyspace, table, data, name=None, value=None):
        if table == self.requests_table:
            self.requests[data['request_id']] = data
        elif table == self.results_table:
            self.results[data['request_id']] = data
        elif table == self.group_rules_table:
            self.group_rules[data['id']] = data
        elif table == self.groups_table:
            self.groups[data['id']] = data
        elif table == self.resources_table:
            self.resources[data['id']] = data
        elif table == self.stacks_table:
            self.stacks[data['id']] = data
        elif table == self.stack_id_map_table:
            self.stack_id_map[data['request_id']] = data

    def delete_atom(self, keyspace, table, pk_name, pk_value):
        if table == self.requests_table:
            if pk_value in self.requests.keys():
                del self.requests[pk_value]
        elif table == self.groups_table:
            if pk_value in self.groups.keys():
                del self.groups[pk_value]
        elif table == self.results_table:
            if pk_value in self.results.keys():
                del self.results[pk_value]

    def read_row(self, keyspace, table, pk_name, pk_value):
        row = {"result": {}}

        if table == self.requests_table:
            if pk_value in self.requests.keys():
                row["result"]["row 0"] = copy.deepcopy(self.requests[pk_value])
        elif table == self.results_table:
            if pk_value in self.results.keys():
                row["result"]["row 0"] = copy.deepcopy(self.results[pk_value])
        elif table == self.resources_table:
            if pk_value in self.resources.keys():
                row["result"]["row 0"] = copy.deepcopy(self.resources[pk_value])
        elif table == self.group_rules_table:
            if pk_value in self.group_rules.keys():
                row["result"]["row 0"] = copy.deepcopy(self.group_rules[pk_value])
        elif table == self.stack_id_map_table:
            if pk_value in self.stack_id_map.keys():
                row["result"]["row 0"] = copy.deepcopy(self.stack_id_map[pk_value])
        elif table == self.stacks_table:
            if pk_value in self.stacks.keys():
                row["result"]["row 0"] = copy.deepcopy(self.stacks[pk_value])

        return row

    def create_lock(self, _key):
        return "$x--0000000000"

    def delete_lock(self, _key):
        pass
