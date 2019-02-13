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
from valet.engine.resource_manager.resources.numa import NUMA


class GroupResource(object):
    """Container for all resource group includes

    affinity, diversity, quorum-diversity, exclusivity, host-aggregate and availability.
    """

    def __init__(self):
        self.name = None

        self.group_type = "aggr"
        self.factory = "nova"
        self.level = "host"

        self.metadata = {}

        self.original_num_of_placed_servers = 0
        self.num_of_placed_servers = 0

        # key = host (host or rack), value = num_of_placed_servers
        self.num_of_placed_servers_of_host = {}


class HostResource(object):
    """Container for hosting resource (host, rack)."""

    def __init__(self):
        # Host info
        self.host_name = None

        self.host_memberships = {}              # all mapped groups to host

        self.host_avail_vCPUs = 0               # remaining vCPUs after overcommit
        self.host_avail_mem = 0                 # remaining mem cap after
        self.host_avail_local_disk = 0          # remaining local disk cap after overcommit

        self.NUMA = None

        self.host_num_of_placed_servers = 0     # the number of vms currently placed in this host

        # If the host type is not determined yet,
        # provide possible host types.
        self.candidate_host_types = {}
        self.old_candidate_host_types = {}      # For rollback

        # To track newly added host types.
        self.new_host_aggregate_list = []

        # Rack info
        self.rack_name = None                   # where this host is located

        self.rack_memberships = {}

        self.rack_avail_vCPUs = 0
        self.rack_avail_mem = 0
        self.rack_avail_local_disk = 0

        self.rack_num_of_placed_servers = 0

        # To track newly added host types.
        self.new_rack_aggregate_list = []

        self.level = None     # level of placement

        self.sort_base = 0    # order to place

    def get_host_type(self, _ha, _host_types):
        """Take host-aggregate group and
        return default host type of the host-aggregate.
        """

        host_type = None

        if _host_types is None:
            return host_type

        host_type_list = _host_types[_ha.name]
        for ht in host_type_list:
            if "default" in ht.keys():
                host_type = ht
                break

        return host_type

    def adjust_avail_resources(self, _ha):
        """Take host-aggregate group and
           add it to host/rack memberships and
           adjust the amount of available resources based on
           the corresponding host type.
        """

        if _ha.name not in self.host_memberships.keys():
            self.host_memberships[_ha.name] = _ha
            self.new_host_aggregate_list.append(_ha.name)
        if _ha.name not in self.rack_memberships.keys():
            self.rack_memberships[_ha.name] = _ha
            self.new_rack_aggregate_list.append(_ha.name)

        host_type = self.get_host_type(_ha, self.candidate_host_types)

        self.host_avail_vCPUs = host_type["avail_vCPUs"]
        self.host_avail_mem = host_type["avail_mem"]
        self.host_avail_local_disk = host_type["avail_local_disk"]

        self.NUMA = NUMA(numa=host_type["NUMA"])

        if self.candidate_host_types is not None:
            for htk, htl in self.candidate_host_types.iteritems():
                if htk == "mockup":
                    self.rack_avail_vCPUs -= htl[0]["avail_vCPUs"]
                    self.rack_avail_mem -= htl[0]["avail_mem"]
                    self.rack_avail_local_disk -= htl[0]["avail_local_disk"]

                    self.rack_avail_vCPUs += self.host_avail_vCPUs
                    self.rack_avail_mem += self.host_avail_mem
                    self.rack_avail_local_disk += self.host_avail_local_disk
                   
                    break

    def adjust_avail_rack_resources(self, _ha, _cpus, _mem, _disk):
        """Take host-aggregate group and the amount of available resources
           add the group into rack membership and
           adjust the amount of available rack resources.
        """

        if _ha.name not in self.rack_memberships.keys():
            self.rack_memberships[_ha.name] = _ha
            self.new_rack_aggregate_list.append(_ha.name)

        self.rack_avail_vCPUs = _cpus
        self.rack_avail_mem = _mem
        self.rack_avail_local_disk = _disk

    def rollback_avail_resources(self, _ha):
        if _ha.name in self.new_host_aggregate_list:
            del self.host_memberships[_ha.name]
            self.new_host_aggregate_list.remove(_ha.name)
        if _ha.name in self.new_rack_aggregate_list:
            del self.rack_memberships[_ha.name]
            self.new_rack_aggregate_list.remove(_ha.name)

        host_type = self.get_host_type(_ha, self.old_candidate_host_types)

        if self.old_candidate_host_types is not None:
            for htk, htl in self.old_candidate_host_types.iteritems():
                if htk == "mockup":
                    self.host_avail_vCPUs = htl[0]["avail_vCPUs"]
                    self.host_avail_mem = htl[0]["avail_mem"]
                    self.host_avail_local_disk = htl[0]["avail_local_disk"]

                    self.NUMA = NUMA(numa=htl[0]["NUMA"])

                    self.rack_avail_vCPUs -= host_type["avail_vCPUs"]
                    self.rack_avail_mem -= host_type["avail_mem"]
                    self.rack_avail_local_disk -= host_type["avail_local_disk"]

                    self.rack_avail_vCPUs += self.host_avail_vCPUs
                    self.rack_avail_mem += self.host_avail_mem
                    self.rack_avail_local_disk += self.host_avail_local_disk

                    break

    def rollback_avail_rack_resources(self, _ha, _cpus, _mem, _disk):
        if _ha.name in self.new_rack_aggregate_list:
            del self.rack_memberships[_ha.name]
            self.new_rack_aggregate_list.remove(_ha.name)

        self.rack_avail_vCPUs = _cpus
        self.rack_avail_mem = _mem
        self.rack_avail_local_disk = _disk

    def get_resource_name(self, _level):
        name = "unknown"

        if _level == "rack":
            name = self.rack_name
        elif _level == "host":
            name = self.host_name

        return name

    def get_vcpus(self, _level):
        avail_vcpus = 0

        if _level == "rack":
            avail_vcpus = self.rack_avail_vCPUs
        elif _level == "host":
            avail_vcpus = self.host_avail_vCPUs

        return avail_vcpus

    def get_mem(self, _level):
        avail_mem = 0

        if _level == "rack":
            avail_mem = self.rack_avail_mem
        elif _level == "host":
            avail_mem = self.host_avail_mem

        return avail_mem

    def get_local_disk(self, _level):
        avail_local_disk = 0

        if _level == "rack":
            avail_local_disk = self.rack_avail_local_disk
        elif _level == "host":
            avail_local_disk = self.host_avail_local_disk

        return avail_local_disk

    def get_memberships(self, _level):
        memberships = None

        if _level == "rack":
            memberships = self.rack_memberships
        elif _level == "host":
            memberships = self.host_memberships

        return memberships

    def get_all_memberships(self, _level):
        memberships = {}

        if _level == "rack":
            for mk, m in self.rack_memberships.iteritems():
                memberships[mk] = m
            for mk, m in self.host_memberships.iteritems():
                memberships[mk] = m
        elif _level == "host":
            for mk, m in self.host_memberships.iteritems():
                memberships[mk] = m

        return memberships

    def get_num_of_placed_servers(self, _level):
        num_of_servers = 0

        if _level == "rack":
            num_of_servers = self.rack_num_of_placed_servers
        elif _level == "host":
            num_of_servers = self.host_num_of_placed_servers

        return num_of_servers
