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
import json
import re
import six

from valet.engine.app_manager.app_parser import Parser
from valet.engine.app_manager.group import Group
from valet.engine.app_manager.server import Server


class App(object):
    """Container to deliver the status of request."""

    def __init__(self, _req_id, _use_dha, _logger):

        self.last_req_id = _req_id

        self.datacenter_id = None

        # stack_id given from the platform (e.g., OpenStack)
        self.app_id = None

        # stack_name as datacenter_id + ":" + tenant_id + ":" + vf_module_name 
        self.app_name = None

        self.tenant_id = None

        # Info for group rule scope
        self.service_instance_id = None
        self.vnf_instance_id = None
        self.vnf_instance_name = None

        # Stack resources. key = server's orch_id
        self.stack = {}

        self.resource = None

        self.logger = _logger

        self.parser = Parser(self.logger)

        self.groups = {}   # all valet groups used in this app
        self.servers = {}   # requested servers (e.g., VMs)

        # Store prior server info.
        self.prior_servers = {}

        self.status = "ok"

        self.state = "plan"

        self.prior_state = "unknown"

        # Check if do not want rollback for create
        self.suppress_rollback = False

        # For placement optimization
        self.total_CPU = 0
        self.total_mem = 0
        self.total_local_vol = 0
        self.optimization_priority = None

        self.use_dha = _use_dha

    def set_resource(self, _resource):
        self.resource = _resource

    def init_for_create(self, _req):
        """Validate and init app info based on the given request."""

        self.state = "create"

        if "datacenter" in _req.keys():
            if "id" in _req["datacenter"].keys():
                if _req["datacenter"]["id"] is not None:
                    self.datacenter_id = _req["datacenter"]["id"].strip()
                else:
                    self.status = "datacenter_id is None"
                    return
            else:
                self.status = "no datacenter_id in request"
                return

            if "url" in _req["datacenter"].keys():
                if _req["datacenter"]["url"] is not None:
                    if not self._match_url(_req["datacenter"]["url"].strip()):
                        self.status = "mal-formed url"
                        return
                else:
                    self.status = "url is None"
                    return
            else:
                self.status = "no url in request"
                return
        else:
            self.status = "no datacenter info in request"
            return

        if "tenant_id" in _req.keys():
            if _req["tenant_id"] is not None:
                self.tenant_id = _req["tenant_id"]
            else:
                self.status = "tenant_id is None"
                return
        else:
            self.status = "no tenant_id in request"
            return

        if "service_instance_id" in _req.keys():
            if _req["service_instance_id"] is not None:
                self.service_instance_id = _req["service_instance_id"]
            else:
                self.status = "service_id is None"
                return
        else:
            self.status = "no service_instance_id in request"
            return

        if "vnf_instance_id" in _req.keys():
            if _req["vnf_instance_id"] is not None:
                self.vnf_instance_id = _req["vnf_instance_id"]
            else:
                self.status = "vnf_id is None"
                return
        else:
            self.status = "no vnf_instance_id in request"
            return

        if "vnf_instance_name" in _req.keys():
            if _req["vnf_instance_name"] is not None:
                self.vnf_instance_name = _req["vnf_instance_name"]
            else:
                self.status = "vnf_name is None"
                return
        else:
            self.status = "no vnf_instance_name in request"
            return

        if "stack_name" in _req.keys():
            if _req["stack_name"] is not None:
                self.app_name = self.datacenter_id + ":" + self.tenant_id + ":" + _req["stack_name"].strip()
            else:
                self.status = "stack_name is None"
                return
        else:
            self.status = "no stack_name in request"
            return

        if "stack" in _req.keys():
            self.stack = self._validate_stack(_req["stack"])
        else:
            self.status = "no stack in request"
            return

    def init_for_delete(self, _req):
        """Validate and init app info for marking delete."""

        self.state = "delete"

        if "datacenter" in _req.keys():
            if "id" in _req["datacenter"].keys():
                if _req["datacenter"]["id"] is not None:
                    self.datacenter_id = _req["datacenter"]["id"].strip()
                else:
                    self.status = "datacenter_id is None"
                    return
            else:
                self.status = "no datacenter_id in request"
                return
        else:
            self.status = "no datacenter info in request"
            return

        if "tenant_id" in _req.keys():
            if _req["tenant_id"] is not None:
                self.tenant_id = _req["tenant_id"]
            else:
                self.status = "tenant_id is None"
                return
        else:
            self.status = "no tenant_id in request"
            return

        if "stack_name" in _req.keys():
            if _req["stack_name"] is not None:
                self.app_name = self.datacenter_id + ":" + self.tenant_id + ":" + _req["stack_name"].strip()
            else:
                self.status = "stack_name is None"
                return
        else:
            self.status = "no stack_name in request"
            return

    def init_for_confirm(self, _req):
        """Validate and init app info for confirm."""

        # Tempoary state and will depends on prior state
        self.state = "confirm"

        if "stack_id" in _req.keys():
            if _req["stack_id"] is not None:
                stack_id = _req["stack_id"].strip()

                stack_id_elements = stack_id.split('/', 1)
                if len(stack_id_elements) > 1:
                    self.app_id = stack_id_elements[1]
                else:
                    self.app_id = stack_id

                self.logger.debug("stack_id = " + self.app_id)

            else:
                self.status = "null stack_id in request"
                return
        else:
            self.status = "no stack_id in request"
            return

    def init_for_rollback(self, _req):
        """Validate and init app info for rollback."""

        # Tempoary state and will depends on prior state
        self.state = "rollback"

        if "stack_id" in _req.keys():
            if _req["stack_id"] is not None:
                stack_id = _req["stack_id"].strip()

                stack_id_elements = stack_id.split('/', 1)
                if len(stack_id_elements) > 1:
                    self.app_id = stack_id_elements[1]
                else:
                    self.app_id = stack_id

                self.logger.debug("stack_id = " + self.app_id)
            else:
                # If the stack fails, stack_id can be null.
                self.app_id = "none"

                self.logger.debug("stack_id = None")
        else:
            self.status = "no stack_id in request"
            return

        if "suppress_rollback" in _req.keys():
            self.suppress_rollback = _req["suppress_rollback"]

        if "error_message" in _req.keys():
            # TODO(Gueyoung): analyze the error message.

            if _req["error_message"] is None:
                self.logger.warning("error message from platform: none")
            else:
                self.logger.warning("error message from platform:" + _req["error_message"])

    def init_prior_app(self, _prior_app):
        """Init with the prior app info."""

        self.datacenter_id = _prior_app.get("datacenter")

        self.app_name = _prior_app.get("stack_name")

        if _prior_app["uuid"] != "none":
            # Delete case.
            self.app_id = _prior_app.get("uuid")

        self.tenant_id = _prior_app.get("tenant_id")

        metadata = json.loads(_prior_app.get("metadata"))
        self.service_instance_id = metadata.get("service_instance_id")
        self.vnf_instance_id = metadata.get("vnf_instance_id")
        self.vnf_instance_name = metadata.get("vnf_instance_name")

        self.servers = json.loads(_prior_app.get("servers"))

        prior_state = _prior_app.get("state")

        if self.state == "confirm":
            if prior_state == "create":
                self.state = "created"
            elif prior_state == "delete":
                self.state = "deleted"
        elif self.state == "rollback":
            if prior_state == "create":
                if self.suppress_rollback and self.app_id != "none":
                    self.state = "created"
                else:
                    self.state = "deleted"

            if prior_state == "delete":
                self.state = "created"
        elif self.state == "delete":
            self.prior_state = prior_state
            self.prior_servers = copy.deepcopy(self.servers)
        else:
            self.status = "unknown state"

    def _validate_stack(self, _stack):
        """Check if the stack is for Valet to make decision.

        And, check if the format is correct.
        """

        if len(_stack) == 0 or "resources" not in _stack.keys():
            self.status = "na: no resource in stack"
            self.logger.warning("non-applicable to valet: no resource in stack")
            return {}

        stack = {}

        for rk, r in _stack["resources"].iteritems():
            if "type" not in r.keys():
                self.status = "type key is missing in stack"
                return None

            if r["type"] == "OS::Nova::Server":
                if "properties" not in r.keys():
                    self.status = "properties key is missing in stack"
                    return None

                if "name" not in r["properties"].keys():
                    self.status = "name property is missing in stack"
                    return None

                if r["properties"]["name"] is None:
                    self.status = "name property is none"
                    return None

                if "flavor" not in r["properties"].keys():
                    self.status = "flavor property is missing in stack"
                    return None

                if r["properties"]["flavor"] is None:
                    self.status = "flavor property is none"
                    return None

                stack[rk] = r

        if len(stack) == 0:
            self.status = "na: no server resource in stack"
            self.logger.warning("non-applicable to valet: no server resource in stack")
            return {}

        first_resource = stack[stack.keys()[0]]
        apply_valet = False

        # To apply Valet decision, availability_zone must exist.
        # And its value contains host variable as a list element.
        if "availability_zone" in first_resource["properties"].keys():
            az_value = first_resource["properties"]["availability_zone"]
            if isinstance(az_value, list):
                apply_valet = True

        for rk, r in stack.iteritems():
            if apply_valet:
                if "availability_zone" not in r["properties"].keys():
                    self.status = "az is missing in stack for valet"
                    return None
                else:
                    az_value = r["properties"]["availability_zone"]
                    if not isinstance(az_value, list):
                        self.status = "host variable is missing in stack for valet"
                        return None

                    if az_value[0] in ("none", "None") or az_value[1] in ("none", "None"):
                        self.status = "az value is missing in stack"
                        return None
            else:
                if "availability_zone" in r["properties"].keys():
                    az_value = r["properties"]["availability_zone"]
                    if isinstance(az_value, list):
                        self.status = "host variable exists in stack for non-valet application"
                        return None

        if not apply_valet:
            self.status = "na: pass valet"
            self.logger.warning("non-applicable to valet")
            return {}
        else:
            return stack

    def init_valet_groups(self):
        """Create Valet groups from input request."""

        for rk, r in self.stack.iteritems():
            properties = r.get("properties", {})
            metadata = properties.get("metadata", {})

            if len(metadata) > 0:
                valet_rules = metadata.get("valet_groups", None)

                if valet_rules is not None and valet_rules != "":
                    rule_list = []
                    if isinstance(valet_rules, six.string_types):
                        rules = valet_rules.split(",")
                        for gr in rules:
                            rule_list.append(gr.strip())
                    else:
                        self.status = "incorrect valet group metadata format"
                        self.logger.error(self.status)
                        return

                    # Check rule validation of valet_groups.
                    self.status = self.resource.check_valid_rules(self.tenant_id,
                                                                  rule_list,
                                                                  use_ex=self.use_dha)
                    if self.status != "ok":
                        self.logger.error(self.status)
                        return

                    self.status = self._make_valet_groups(properties.get("name"),
                                                          properties["availability_zone"][0],
                                                          rule_list)
                    if self.status != "ok":
                        self.logger.error(self.status)
                        return

            # Check and create server groups if they do not exist.
            scheduler_hints = properties.get("scheduler_hints", {})
            if len(scheduler_hints) > 0:
                for hint_key in scheduler_hints.keys():
                    if hint_key == "group":
                        hint = scheduler_hints[hint_key]
                        self.status = self._make_group(properties.get("name"), hint)
                        if self.status != "ok":
                            self.logger.error(self.status)
                            return

    def _make_valet_groups(self, _rk, _az, _rule_list):
        """Create Valet groups that each server is involved."""

        for rn in _rule_list:
            rule = self.resource.group_rules[rn]

            # Valet group naming convention.
            # It contains datacenter id and availability_zone
            # followed by service id and vnf id
            # depending on scope.
            # And concatenate rule name.
            # Exception: quorum-diversity

            group_id = self.datacenter_id + ":"

            if rule.rule_type != "quorum-diversity":
                group_id += _az + ":"

            if rule.app_scope == "lcp":
                group_id += rn
            elif rule.app_scope == "service":
                group_id += self.service_instance_id + ":" + rn
            elif rule.app_scope == "vnf":
                group_id += self.service_instance_id + ":" + self.vnf_instance_id + ":" + rn
            else:
                return "unknown app_scope value"

            if group_id in self.groups.keys():
                group = self.groups[group_id]
            else:
                group = Group(group_id)
                group.group_type = rule.rule_type
                group.factory = "valet"
                group.level = rule.level

                self.groups[group_id] = group

            group.server_list.append(self.app_name + ":" + _rk)

        return "ok"

    def _make_group(self, _rk, _group_hint):
        """Create the group request based on scheduler hint."""

        if isinstance(_group_hint, dict):
            # _group_hint is a single key/value pair
            g = _group_hint[_group_hint.keys()[0]]

            r_type = g.get("type", "none")
            if r_type != "OS::Nova::ServerGroup":
                return "support only ServerGroup resource"

            properties = g.get("properties", {})
            if len(properties) == 0:
                return "no properties"

            group_name = properties.get("name", None)
            if group_name is None:
                return "no group name"
            group_name = group_name.strip()

            policies = properties.get("policies", [])
            if len(policies) == 0:
                return "no policy of the group"

            if len(policies) > 1:
                return "multiple policies"

            # TODO: exclude soft-affinity and soft-anti-affinity?

            if group_name in self.groups.keys():
                group = self.groups[group_name]
            else:
                group = Group(group_name)

                policy = policies[0].strip()
                if policy == "anti-affinity":
                    group_type = "diversity"
                else:
                    group_type = policy

                group.group_type = group_type
                group.factory = "server-group"
                group.level = "host"

                self.groups[group_name] = group
        else:
            # group hint is uuid string.
            rg = self.resource.get_group_by_uuid(_group_hint)
            if rg is None:
                return "unknown group found while making group"

            # TODO: exclude soft-affinity and soft-anti-affinity?

            if rg.name in self.groups.keys():
                group = self.groups[rg.name]
            else:
                group = Group(rg.name)

                group.group_type = rg.group_type
                group.factory = rg.factory
                group.level = "host"

                self.groups[rg.name] = group

        if group is not None:
            group.server_list.append(self.app_name + ":" + _rk)

        return "ok"

    def parse(self):
        """Extract servers and merge groups from stack for search."""

        (self.servers, self.groups) = self.parser.set_servers(self.app_name,
                                                              self.stack,
                                                              self.groups)

        if len(self.servers) == 0 and len(self.groups) == 0:
            self.status = "parse error for " + self.app_name + ": " + self.parser.status
            return False

        return True

    def set_weight(self):
        """Set relative weight of each servers and groups."""

        for _, s in self.servers.iteritems():
            self._set_server_weight(s)

        for _, g in self.groups.iteritems():
            self._set_server_weight(g)

        for _, g in self.groups.iteritems():
            self._set_group_resource(g)

        for _, g in self.groups.iteritems():
            self._set_group_weight(g)

    def _set_server_weight(self, _v):
        """Set relative weight of each server against available resource amount."""

        if isinstance(_v, Group):
            for _, sg in _v.subgroups.iteritems():
                self._set_server_weight(sg)
        else:
            if self.resource.CPU_avail > 0:
                _v.vCPU_weight = float(_v.vCPUs) / float(self.resource.CPU_avail)
            else:
                _v.vCPU_weight = 1.0
            self.total_CPU += _v.vCPUs

            if self.resource.mem_avail > 0:
                _v.mem_weight = float(_v.mem) / float(self.resource.mem_avail)
            else:
                _v.mem_weight = 1.0
            self.total_mem += _v.mem

            if self.resource.local_disk_avail > 0:
                _v.local_volume_weight = float(_v.local_volume_size) / float(self.resource.local_disk_avail)
            else:
                if _v.local_volume_size > 0:
                    _v.local_volume_weight = 1.0
                else:
                    _v.local_volume_weight = 0.0
            self.total_local_vol += _v.local_volume_size

    def _set_group_resource(self, _g):
        """Sum up amount of resources of servers for each affinity group."""

        if isinstance(_g, Server):
            return

        for _, sg in _g.subgroups.iteritems():
            self._set_group_resource(sg)
            _g.vCPUs += sg.vCPUs
            _g.mem += sg.mem
            _g.local_volume_size += sg.local_volume_size

    def _set_group_weight(self, _group):
        """Set relative weight of each affinity group against available resource amount."""

        if self.resource.CPU_avail > 0:
            _group.vCPU_weight = float(_group.vCPUs) / float(self.resource.CPU_avail)
        else:
            if _group.vCPUs > 0:
                _group.vCPU_weight = 1.0
            else:
                _group.vCPU_weight = 0.0

        if self.resource.mem_avail > 0:
            _group.mem_weight = float(_group.mem) / float(self.resource.mem_avail)
        else:
            if _group.mem > 0:
                _group.mem_weight = 1.0
            else:
                _group.mem_weight = 0.0

        if self.resource.local_disk_avail > 0:
            _group.local_volume_weight = float(_group.local_volume_size) / float(self.resource.local_disk_avail)
        else:
            if _group.local_volume_size > 0:
                _group.local_volume_weight = 1.0
            else:
                _group.local_volume_weight = 0.0

        for _, sg in _group.subgroups.iteritems():
            if isinstance(sg, Group):
                self._set_group_weight(sg)

    def set_optimization_priority(self):
        """Determine the optimization priority among different types of resources."""

        if len(self.groups) == 0 and len(self.servers) == 0:
            return

        if self.resource.CPU_avail > 0:
            app_cpu_weight = float(self.total_CPU) / float(self.resource.CPU_avail)
        else:
            if self.total_CPU > 0:
                app_cpu_weight = 1.0
            else:
                app_cpu_weight = 0.0

        if self.resource.mem_avail > 0:
            app_mem_weight = float(self.total_mem) / float(self.resource.mem_avail)
        else:
            if self.total_mem > 0:
                app_mem_weight = 1.0
            else:
                app_mem_weight = 0.0

        if self.resource.local_disk_avail > 0:
            app_local_vol_weight = float(self.total_local_vol) / float(self.resource.local_disk_avail)
        else:
            if self.total_local_vol > 0:
                app_local_vol_weight = 1.0
            else:
                app_local_vol_weight = 0.0

        opt = [("cpu", app_cpu_weight),
               ("mem", app_mem_weight),
               ("lvol", app_local_vol_weight)]

        self.optimization_priority = sorted(opt, key=lambda resource: resource[1], reverse=True)

    def reset_servers(self):
        """Get servers back from containers (i.e., affinity groups)"""

        servers = []
        for _, g in self.groups.iteritems():
            g.get_servers(servers)

        for s in servers:
            self.servers[s.vid] = s

    def _match_url(self, _url):
        """Check if the URL is a correct form."""

        regex = re.compile(
                r'^(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, _url):
            return True
        else:
            return False
