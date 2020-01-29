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
import six

from valet.engine.app_manager.group import FLAVOR_TYPES


class Server(object):
    """Container to keep requested server (e.g., VM)."""

    def __init__(self, _id, _orch_id):
        """Define server info and parameters."""

        # ID consists of stack_name + ":" + server_name,
        # where stack_name = datacenter_id + ":" + tenant_id + ":" + vf_module_name
        self.vid = _id

        # ID in stack
        self.orch_id = _orch_id

        # one given in Heat stack
        self.name = None

        # Affinity group object
        self.surgroup = None

        self.diversity_groups = {}
        self.quorum_diversity_groups = {}
        self.exclusivity_groups = {}

        self.availability_zone = None

        self.flavor = None
        self.image = None

        self.vCPUs = 0
        self.mem = 0                  # MB
        self.local_volume_size = 0    # GB
        self.extra_specs_list = []

        self.vCPU_weight = -1
        self.mem_weight = -1
        self.local_volume_weight = -1

        # To return placement.
        # If stack is nested, should point the index to distinguish
        self.host_assignment_variable = None
        self.host_assignment_inx = -1

        # Placement result
        self.host_group = None    # e.g., rack
        self.host = None
        self.numa = None

        # Request state is 'create', 'migrate', 'rebuild', 'delete'
        # 'created', 'migrated', 'rebuilt'
        self.state = "plan"

        # To inform if the current placement violates rules and requirements
        self.status = "valid"

        self.sort_base = -1

    def get_exclusivities(self, _level):
        """Return exclusivity group requested with a level (host or rack).

        Note: each server must have a single exclusivity group of the level.
        """

        exclusivities = {}

        for exk, group in self.exclusivity_groups.items():
            if group.level == _level:
                exclusivities[exk] = group

        return exclusivities

    def need_numa_alignment(self):
        """Check if this server requires NUMA alignment."""

        if len(self.extra_specs_list) > 0:
            for es in self.extra_specs_list:
                for key, req in six.iteritems(es):
                    if key == "hw:numa_nodes" and int(req) == 1:
                        return True

        return False

    def get_flavor_types(self):
        flavor_type_list = []

        for extra_specs in self.extra_specs_list:
            for k, v in extra_specs.items():
                k_elements = k.split(':')
                if len(k_elements) > 1:
                    if k_elements[0] == "aggregate_instance_extra_specs":
                        if k_elements[1].lower() in FLAVOR_TYPES:
                            if v == "true":
                                flavor_type_list.append(k_elements[1])

        return flavor_type_list

    def get_json_info(self):
        """Format server info as JSON."""

        if self.surgroup is None:
            surgroup_id = "none"
        else:
            surgroup_id = self.surgroup.vid

        diversity_groups = []
        for divk in self.diversity_groups.keys():
            diversity_groups.append(divk)

        quorum_diversity_groups = []
        for divk in self.quorum_diversity_groups.keys():
            quorum_diversity_groups.append(divk)

        exclusivity_groups = []
        for exk in self.exclusivity_groups.keys():
            exclusivity_groups.append(exk)

        if self.availability_zone is None:
            availability_zone = "none"
        else:
            availability_zone = self.availability_zone

        if self.host_group is None:
            host_group = "none"
        else:
            host_group = self.host_group

        if self.numa is None:
            numa = "none"
        else:
            numa = self.numa

        return {'name': self.name,
                'orch_id': self.orch_id,
                'surgroup': surgroup_id,
                'diversity_groups': diversity_groups,
                'quorum_diversity_groups': quorum_diversity_groups,
                'exclusivity_groups': exclusivity_groups,
                'availability_zones': availability_zone,
                'extra_specs_list': self.extra_specs_list,
                'flavor': self.flavor,
                'image': self.image,
                'cpus': self.vCPUs,
                'mem': self.mem,
                'local_volume': self.local_volume_size,
                'host_group': host_group,
                'host': self.host,
                'numa': numa,
                'state': self.state,
                'status': self.status}
