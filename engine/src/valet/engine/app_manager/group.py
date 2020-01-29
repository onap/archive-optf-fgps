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


LEVEL = ["host", "rack", "cluster"]

FLAVOR_TYPES = ["gv", "nv", "nd", "ns", "ss"]


class Group(object):
    """Container to keep requested valet groups.

    TODO(Gueyoung): create parent class to make common functions
    """

    def __init__(self, _id):
        """Define group info and parameters."""

        # ID consists of
        # datacenter_id + [service_instance_id] + [vnf_instance_id] + rule_name
        self.vid = _id

        # Type is either affinity, diversity, quorum_diversity, or exclusivity
        self.group_type = None

        self.factory = None

        # Level is host or rack
        self.level = None

        # To build containment tree
        self.surgroup = None    # parent 'affinity' object
        self.subgroups = {}    # child affinity group (or server) objects

        # Group objects of this container
        self.diversity_groups = {}
        self.quorum_diversity_groups = {}
        self.exclusivity_groups = {}

        self.availability_zone_list = []

        self.extra_specs_list = []

        self.vCPUs = 0
        self.mem = 0                   # MB
        self.local_volume_size = 0     # GB

        self.vCPU_weight = -1
        self.mem_weight = -1
        self.local_volume_weight = -1

        # To record which servers (e.g., VMs) in given request are assigned
        # to this group.
        self.server_list = []

        self.sort_base = -1

    def get_exclusivities(self, _level):
        """Return exclusivity group requested with a level (host or rack).

        Note: each affinity group must have a single exclusivity group of the level.
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
                    if key == "hw:numa_nodes" and req == 1:
                        return True

        return False

    def is_parent_affinity(self, _vk):
        """Check recursively if _vk is located in the group."""

        exist = False

        for sgk, sg in self.subgroups.items():
            if sgk == _vk:
                exist = True
                break

            if isinstance(sg, Group):
                if sg.is_parent_affinity(_vk):
                    exist = True
                    break

        return exist

    def get_servers(self, _servers):
        """Get all child servers."""

        for _, sg in self.subgroups.items():
            if isinstance(sg, Group):
                sg.get_servers(_servers)
            else:
                if sg not in _servers:
                    _servers.append(sg)

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
