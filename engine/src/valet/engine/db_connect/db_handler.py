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
import operator

from valet.engine.db_connect.locks import Locks, now


class DBHandler(object):

    def __init__(self, _db, _config, _logger):
        self.keyspace = _config.get("keyspace")
        self.requests_table = _config.get("requests_table")
        self.results_table = _config.get("results_table")
        self.group_rules_table = _config.get("group_rules_table")
        self.groups_table = _config.get("groups_table")
        self.stacks_table = _config.get("stacks_table")
        self.resources_table = _config.get("resources_table")
        self.stack_id_map_table = _config.get("stack_id_map_table")
        self.regions_table = _config.get("regions_table")

        self.db = _db

        self.logger = _logger

    def get_requests(self):
        """Get requests from valet-api."""

        request_list = []

        try:
            rows = self.db.read_all_rows(self.keyspace, self.requests_table)
        except Exception as e:
            self.logger.error("DB: while reading requests: " + str(e))
            return []

        if rows is not None and len(rows) > 0:
            for key, row in rows.items():
                if key == "status":
                    if row == "FAILURE":
                        self.logger.error("DB: Failure in " + self.requests_table)
                        return []
                    continue
                elif key == "error":
                    continue
                elif key == "result":
                    for _, dbrow in row.items():
                        request_list.append(dbrow)

            if len(request_list) > 0:
                # NOTE(Gueyoung): Sort by timestamp if timestamp is based UDT.
                # Currently, ping's timestamp is always -1, while all others 0.
                # This is to provide the priority to ping request.
                request_list.sort(key=operator.itemgetter("timestamp"))

        return request_list

    def return_request(self, _req_id, _status, _result):
        """Finalize the request by

        Create result in results table and delete handled request from requests table.
        """

        # TODO(Gueyoung): avoid duplicated results.

        # Wait randomly with unique seed (Valet instance ID).
        # random.seed(_seed)
        # r = random.randint(1, 100)
        # delay = float(r) / 100.0
        # time.sleep(delay)

        if not self._create_result(_req_id, _status, _result):
            return False

        if not self._delete_request(_req_id):
            return False

        return True

    def get_results(self):
        """Get results."""

        result_list = []

        try:
            rows = self.db.read_all_rows(self.keyspace, self.results_table)
        except Exception as e:
            self.logger.error("DB: while reading results: " + str(e))
            return None

        if rows is not None and len(rows) > 0:
            for key, row in rows.items():
                if key == "status":
                    continue
                elif key == "error":
                    continue
                elif key == "result":
                    for _, dbrow in row.items():
                        result_list.append(dbrow)

        return result_list

    def _create_result(self, _req_id, _status, _result):
        """Return result of request by putting it into results table."""

        data = {
            'request_id': _req_id,
            'status': json.dumps(_status),
            'result': json.dumps(_result),
            'timestamp': now()
        }
        try:
            self.db.insert_atom(self.keyspace, self.results_table, data)
        except Exception as e:
            self.logger.error("DB: while putting placement result: " + str(e))
            return False

        return True

    def _delete_request(self, _req_id):
        """Delete finished request."""

        try:
            self.db.delete_atom(self.keyspace, self.requests_table,
                                'request_id', _req_id)
        except Exception as e:
            self.logger.error("DB: while deleting handled request: " + str(e))
            return False

        return True

    def clean_expired_regions(self):
        """Delete regions from the regions table that have expired.

        Return the list of locked regions."""

        locked_regions = []

        try:
            result = self.db.read_row(self.keyspace, self.regions_table, None, None)["result"]
        except Exception as e:
            self.logger.error("DB: while reading locked regions: " + str(e))
            return None

        for _, data in sorted(result.items()):
            if int(data["expire_time"]) < now():

                self.logger.warning("lock on %s has timed out and is revoked" % data["region_id"])

                Locks.unlock(self, data["region_id"])

                if not self.delete_region(data["region_id"]):
                    return None
            else:
                locked_regions.append(data["region_id"])

        return locked_regions

    def delete_region(self, region_id):
        """Delete from regions table."""

        try:
            self.db.delete_atom(self.keyspace, self.regions_table,
                                'region_id', region_id)
        except Exception as e:
            self.logger.error("DB: while deleting expired lock: " + str(e))
            return False

        return True

    def add_region(self, region_id, expire_time, update=False):
        """Add/update locking info into region table."""

        data = {
            "region_id":   region_id, 
            "locked_by":   "hostname",
            "expire_time": expire_time
        }

        name = value = None
        if update:
            name = "region_id"
            value = region_id

        try:
            self.db.insert_atom(self.keyspace, self.regions_table, data, name, value)
        except Exception as e:
            self.logger.error("DB: while adding locked region: " + str(e))
            return False

        return True

    def create_stack_id_map(self, _req_id, _stack_id):
        """Create request map entry."""

        data = {
            'request_id': _req_id,
            'stack_id': _stack_id
        }
        try:
            self.db.insert_atom(self.keyspace, self.stack_id_map_table, data)
        except Exception as e:
            self.logger.error("DB: while creating request map: " + str(e))
            return False

        return True

    def get_stack_id_map(self, _req_id):
        """Get stack id."""

        try:
            row = self.db.read_row(self.keyspace, self.stack_id_map_table,
                                   "request_id", _req_id)
        except Exception as e:
            self.logger.error("DB: while reading stack_id: " + str(e))
            return None

        if len(row) > 0:
            if "result" in row.keys():
                if len(row["result"]) > 0:
                    return row["result"][list(row["result"])[0]]
                else:
                    return {}
            else:
                return {}
        else:
            return {}

    def delete_stack_id_map(self, _req_id):
        """Delete map of confirmed or rollbacked request."""

        try:
            self.db.delete_atom(self.keyspace, self.stack_id_map_table,
                                'request_id', _req_id)
        except Exception as e:
            self.logger.error("DB: while deleting request id map: " + str(e))
            return False

        return True

    def get_group_rules(self):
        """Get all valet group rules."""

        rule_list = []

        try:
            rows = self.db.read_all_rows(self.keyspace, self.group_rules_table)
        except Exception as e:
            self.logger.error("DB: while reading group rules: " + str(e))
            return None

        if len(rows) > 0:
            for key, row in rows.items():
                if key == "result":
                    for _, dbrow in row.items():
                        rule_list.append(dbrow)

        return rule_list

    def get_group_rule(self, _id):
        """Get valet group rule."""

        try:
            row = self.db.read_row(self.keyspace, self.group_rules_table, "id", _id)
        except Exception as e:
            self.logger.error("DB: while reading group rule: " + str(e))
            return None

        if len(row) > 0:
            if "result" in row.keys():
                if len(row["result"]) > 0:
                    return row["result"][list(row["result"])[0]]
                else:
                    return {}
            else:
                return {}
        else:
            return {}

    def create_group_rule(self, _name, _scope, _type, _level, _members, _desc):
        """Create a group rule."""

        data = {
            'id': _name,
            'app_scope': _scope,
            'type': _type,
            'level': _level,
            'members': json.dumps(_members),
            'description': _desc,
            'groups': json.dumps([]),
            'status': "enabled"
        }
        try:
            self.db.insert_atom(self.keyspace, self.group_rules_table, data)
        except Exception as e:
            self.logger.error("DB: while creating a group rule: " + str(e))
            return False

        return True

    def get_valet_groups(self):
        """Get all valet groups."""

        group_list = []

        try:
            rows = self.db.read_all_rows(self.keyspace, self.groups_table)
        except Exception as e:
            self.logger.error("DB: while reading groups: " + str(e))
            return None

        if len(rows) > 0:
            for key, row in rows.items():
                if key == "result":
                    for _, dbrow in row.items():
                        group_list.append(dbrow)

        return group_list

    def create_valet_group(self, _id, _g_info):
        """Create a group."""

        data = {
            'id': _id,
            'uuid': _g_info.get("uuid"),
            'type': _g_info.get("group_type"),
            'level': _g_info.get("level"),
            'factory': _g_info.get("factory"),
            'rule_id': _g_info.get("rule_id"),
            'metadata': json.dumps(_g_info.get("metadata")),
            'server_list': json.dumps(_g_info.get("server_list")),
            'member_hosts': json.dumps(_g_info.get("member_hosts")),
            'status': _g_info.get("status")
        }
        try:
            self.db.insert_atom(self.keyspace, self.groups_table, data)
        except Exception as e:
            self.logger.error("DB: while creating a group: " + str(e))
            return False

        return True

    def update_valet_group(self, _id, _g_info):
        """Update group."""

        data = {
            'id': _id,
            'uuid': _g_info.get("uuid"),
            'type': _g_info.get("group_type"),
            'level': _g_info.get("level"),
            'factory': _g_info.get("factory"),
            'rule_id': _g_info.get("rule_id"),
            'metadata': json.dumps(_g_info.get("metadata")),
            'server_list': json.dumps(_g_info.get("server_list")),
            'member_hosts': json.dumps(_g_info.get("member_hosts")),
            'status': _g_info.get("status")
        }
        try:
            self.db.insert_atom(self.keyspace, self.groups_table, data,
                                name='id', value=_id)
        except Exception as e:
            self.logger.error("DB: while updating group: " + str(e))
            return False

        return True

    def delete_valet_group(self, _id):
        """Delete finished request."""

        try:
            self.db.delete_atom(self.keyspace, self.groups_table, 'id', _id)
        except Exception as e:
            self.logger.error("DB: while deleting valet group: " + str(e))
            return False

        return True

    def get_resource(self, _dc_id):
        """Get datacenter's resource."""

        try:
            row = self.db.read_row(self.keyspace, self.resources_table, "id", _dc_id)
        except Exception as e:
            self.logger.error("DB: while reading datacenter resource: " + str(e))
            return None

        if len(row) > 0:
            if "result" in row.keys():
                if len(row["result"]) > 0:
                    return row["result"][list(row["result"])[0]]
                else:
                    return {}
            else:
                return {}
        else:
            return {}

    def create_resource(self, _k, _url, _requests, _resource):
        """Create a new resource status."""

        data = {
            'id': _k,
            'url': _url,
            'requests': json.dumps(_requests),
            'resource': json.dumps(_resource)
        }
        try:
            self.db.insert_atom(self.keyspace, self.resources_table, data)
        except Exception as e:
            self.logger.error("DB: while inserting resource status: " + str(e))
            return False

        return True

    def update_resource(self, _k, _url, _requests, _resource):
        """Update resource status."""

        data = {
            'id': _k,
            'url': _url,
            'requests': json.dumps(_requests),
            'resource': json.dumps(_resource)
        }
        try:
            self.db.insert_atom(self.keyspace, self.resources_table, data,
                                name='id', value=_k)
        except Exception as e:
            self.logger.error("DB: while updating resource status: " + str(e))
            return False

        return True

    def get_stack(self, _id):
        """Get stack info."""

        try:
            row = self.db.read_row(self.keyspace, self.stacks_table, 'id', _id)
        except Exception as e:
            self.logger.error("DB: while getting stack info: " + str(e))
            return None

        if len(row) > 0:
            if "result" in row.keys():
                if len(row["result"]) > 0:
                    return row["result"][row["result"].keys()[0]]
                else:
                    return {}
            else:
                return {}
        else:
            return {}

    def create_stack(self, _id, _status, _dc, _name, _uuid,
                     _tenant_id, _metadata,
                     _servers, _old_servers,
                     _state, _old_state):
        """Store new stack info."""

        data = {
            'id': _id,
            'last_status': _status,
            'datacenter': _dc,
            'stack_name': _name,
            'uuid': _uuid,
            'tenant_id': _tenant_id,
            'metadata': json.dumps(_metadata),
            'servers': json.dumps(_servers),
            'prior_servers': json.dumps(_old_servers),
            'state': _state,
            'prior_state': _old_state
        }
        try:
            self.db.insert_atom(self.keyspace, self.stacks_table, data)
        except Exception as e:
            self.logger.error("DB: while storing app: " + str(e))
            return False

        return True

    def delete_stack(self, _id):
        """Delete stack."""

        try:
            self.db.delete_atom(self.keyspace, self.stacks_table, 'id', _id)
        except Exception as e:
            self.logger.error("DB: while deleting app: " + str(e))
            return False

        return True

    def update_stack(self, _id, _status, _dc, _name, _uuid,
                     _tenant_id, _metadata,
                     _servers, _old_servers,
                     _state, _old_state):
        """Store updated stack info."""

        data = {
            'id': _id,
            'last_status': _status,
            'datacenter': _dc,
            'stack_name': _name,
            'uuid': _uuid,
            'tenant_id': _tenant_id,
            'metadata': json.dumps(_metadata),
            'servers': json.dumps(_servers),
            'prior_servers': json.dumps(_old_servers),
            'state': _state,
            'prior_state': _old_state
        }
        try:
            self.db.insert_atom(self.keyspace, self.stacks_table, data,
                                name='id', value=_id)
        except Exception as e:
            self.logger.error("DB: while updating stack: " + str(e))
            return False

        return True
