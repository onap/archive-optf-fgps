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

from valet.engine.resource_manager.resource import Resource
from valet.engine.resource_manager.resources.group_rule import GroupRule
from valet.engine.resource_manager.resources.host_group import HostGroup


class ResourceHandler:
    """Handler for dealing with all existing datacenters and their resources."""

    def __init__(self, _tid, _dbh, _compute, _metadata, _topology,
                 _config, _logger):
        self.end_of_process = False

        self.dbh = _dbh

        self.compute = _compute
        self.metadata = _metadata
        self.topology = _topology

        self.default_cpu_allocation_ratio = _config.get("default_cpu_allocation_ratio")
        self.default_ram_allocation_ratio = _config.get("default_ram_allocation_ratio")
        self.default_disk_allocation_ratio = _config.get("default_disk_allocation_ratio")
        self.batch_sync_interval = _config.get("batch_sync_interval")

        self.group_rules = {}
        self.resource_list = []

        self.logger = _logger

    def load_group_rules_from_db(self):
        """Get all defined valet group rules from DB.

        Note that rules are applied to all datacenters.
        """

        # Init first
        self.group_rules = {}

        rule_list = self.dbh.get_group_rules()
        if rule_list is None:
            return None

        for r in rule_list:
            rule = GroupRule(r.get("id"))

            rule.status = r.get("status")

            rule.app_scope = r.get("app_scope")
            rule.rule_type = r.get("type")
            rule.level = r.get("level")
            rule.members = json.loads(r.get("members"))
            rule.desc = r.get("description")

            self.group_rules[rule.rule_id] = rule

        return "ok"

    def load_group_rule_from_db(self, _id):
        """Get valet group rule from DB."""

        # Init first
        self.group_rules = {}

        r = self.dbh.get_group_rule(_id)
        if r is None:
            return None
        elif len(r) == 0:
            return "rule not found"

        rule = GroupRule(r.get("id"))

        rule.status = r.get("status")

        rule.app_scope = r.get("app_scope")
        rule.rule_type = r.get("type")
        rule.level = r.get("level")
        rule.members = json.loads(r.get("members"))
        rule.desc = r.get("description")

        self.group_rules[rule.rule_id] = rule

        return "ok"

    def create_group_rule(self, _name, _scope, _type, _level, _members, _desc):
        """Create a new group rule in DB."""

        r = self.dbh.get_group_rule(_name)
        if r is None:
            return None
        elif len(r) > 0:
            return "rule already exists"

        if not self.dbh.create_group_rule(_name, _scope, _type, _level,
                                          _members, _desc):
            return None

        return "ok"

    def get_rules(self):
        """Return basic info of valet rules."""

        rule_list = []

        valet_group_list = self.dbh.get_valet_groups()
        if valet_group_list is None:
            return None

        for rk, rule in self.group_rules.items():
            rule_info = self._get_rule(rule)

            for vg in valet_group_list:
                if vg["rule_id"] == rk:
                    gk = vg.get("id")
                    gk_elements = gk.split(":")
                    dc_id = gk_elements[0]

                    if dc_id not in rule_info["regions"]:
                        rule_info["regions"].append(dc_id)

            rule_list.append(rule_info)

        return rule_list

    def _get_rule(self, _rule):
        """Return rule info."""

        rule_info = {}

        rule_info["id"] = _rule.rule_id
        rule_info["type"] = _rule.rule_type
        rule_info["app_scope"] = _rule.app_scope
        rule_info["level"] = _rule.level
        rule_info["members"] = _rule.members
        rule_info["description"] = _rule.desc
        rule_info["status"] = _rule.status
        rule_info["regions"] = []

        return rule_info

    def get_placements_under_rule(self, _rule_name, _resource):
        """Get server placements info under given rule in datacenter."""

        placements = {}

        rule = self.group_rules[_rule_name]

        for gk, g in _resource.groups.items():
            if g.factory == "valet":
                if g.rule.rule_id == _rule_name:
                    placements[gk] = self._get_placements(g, _resource)

        result = {}
        result["id"] = rule.rule_id
        result["type"] = rule.rule_type
        result["app_scope"] = rule.app_scope
        result["level"] = rule.level
        result["members"] = rule.members
        result["description"] = rule.desc
        result["status"] = rule.status
        result["placements"] = placements

        return result

    def _get_placements(self, _g, _resource):
        """Get placement info of servers in group."""

        placements = {}

        for hk, server_list in _g.member_hosts.items():
            for s_info in server_list:
                sid = s_info.get("stack_name") + ":" + s_info.get("name")
                placements[sid] = {}
                placements[sid]["region"] = _resource.datacenter_id

                if hk in _resource.hosts.keys():
                    host = _resource.hosts[hk]

                    placements[sid]["host"] = host.name

                    hg = host.host_group
                    if isinstance(hg, HostGroup) and hg.host_type == "rack":
                        placements[sid]["rack"] = hg.name
                    else:
                        placements[sid]["rack"] = "na"

                    az = host.get_availability_zone()
                    az_name_elements = az.name.split(':', 1)
                    if len(az_name_elements) > 1:
                        az_name = az_name_elements[1]
                    else:
                        az_name = az.name
                    placements[sid]["availability-zone"] = az_name

                elif hk in _resource.host_groups.keys():
                    hg = _resource.host_groups[hk]

                    if hg.host_type == "rack":
                        placements[sid]["rack"] = hg.name

                        for hhk, host in hg.child_resources.items():
                            if host.has_server(s_info):
                                placements[sid]["host"] = host.name

                                az = host.get_availability_zone()
                                az_name_elements = az.name.split(':', 1)
                                if len(az_name_elements) > 1:
                                    az_name = az_name_elements[1]
                                else:
                                    az_name = az.name
                                placements[sid]["availability-zone"] = az_name

                                break
                    else:
                        # TODO(Gueyoung): Look for az, rack and host
                        placements[sid]["availability-zone"] = "na"
                        placements[sid]["rack"] = "na"
                        placements[sid]["host"] = "na"

                else:
                    placements[sid]["availability-zone"] = "na"
                    placements[sid]["rack"] = "na"
                    placements[sid]["host"] = "na"

        return placements

    def load_resource(self, _datacenter):
        """Create a resource for placement decisions

        in a given target datacenter.
        """

        # Init first
        del self.resource_list[:]

        resource = Resource(_datacenter, self.dbh,
                            self.compute, self.metadata, self.topology,
                            self.logger)

        resource.set_config(self.default_cpu_allocation_ratio,
                            self.default_ram_allocation_ratio,
                            self.default_disk_allocation_ratio)

        resource.set_group_rules(self.group_rules)

        status = resource.load_resource_from_db()
        if status is None:
            return False
        elif status != "ok":
            self.logger.warning(status)
            resource.new = True

        self.resource_list.append(resource)

        return True

    def load_resource_with_rule(self, _datacenter):
        """Create and return a resource with valet group rule."""

        # Init first
        del self.resource_list[:]

        resource = Resource(_datacenter, self.dbh,
                            self.compute, self.metadata, self.topology,
                            self.logger)

        resource.set_config(self.default_cpu_allocation_ratio,
                            self.default_ram_allocation_ratio,
                            self.default_disk_allocation_ratio)

        resource.set_group_rules(self.group_rules)

        status = resource.load_resource_from_db()
        if status is None:
            return None
        elif status != "ok":
            return status

        self.resource_list.append(resource)

        return "ok"
