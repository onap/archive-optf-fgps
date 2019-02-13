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

from valet.engine.app_manager.server import Server
from valet.engine.search.filters.aggregate_instance_filter import AggregateInstanceExtraSpecsFilter
from valet.engine.search.filters.cpu_filter import CPUFilter
from valet.engine.search.filters.disk_filter import DiskFilter
from valet.engine.search.filters.mem_filter import MemFilter
from valet.engine.search.filters.numa_filter import NUMAFilter


class DynamicAggregateFilter(object):

    def __init__(self):
        self.name = "dynamic-aggregate"

        self.avail_hosts = {}
        self.avail_groups = {}

        self.aggr_filter = AggregateInstanceExtraSpecsFilter()
        self.cpu_filter = CPUFilter()
        self.mem_filter = MemFilter()
        self.disk_filter = DiskFilter()
        self.numa_filter = NUMAFilter()

        self.status = None

    def init_condition(self):
        self.avail_hosts = {}
        self.avail_groups = {}
        self.status = None

    def check_pre_condition(self, _level, _v, _avail_hosts, _avail_groups):
        if _level == "host" and isinstance(_v, Server):
            self.avail_hosts = _avail_hosts
            self.avail_groups = _avail_groups
            return True
        else:
            return False

    def filter_candidates(self, _level, _v, _candidate_list):
        specified_candidate_list = []     # candidates having specific host type
        unspecified_candidate_list = []   # candidates not having specific host type

        for c in _candidate_list:
            if len(c.candidate_host_types) == 0:
                specified_candidate_list.append(c)
            else:
                unspecified_candidate_list.append(c)

        # Try to use existing hosts that have specific host type
        if len(specified_candidate_list) > 0:
            return specified_candidate_list

        # Take just one candidate
        candidate = unspecified_candidate_list[0]

        # Get the host-aggregate of _v
        flavor_type_list = _v.get_flavor_types()
        if len(flavor_type_list) > 1:
            self.status = "have more than one flavor type"
            return []

        ha = self.avail_groups[flavor_type_list[0]]

        # Add the host-aggregate into host and rack memberships.
        # Adjust host with avail cpus, mem, disk, and numa
        candidate.adjust_avail_resources(ha)

        # Change all others in the same rack.
        for hrk, hr in self.avail_hosts.iteritems():
            if hrk != candidate.host_name:
                if hr.rack_name == candidate.rack_name:
                    hr.adjust_avail_rack_resources(ha, 
                                                   candidate.rack_avail_vCPUs,
                                                   candidate.rack_avail_mem,
                                                   candidate.rack_avail_local_disk)

        # Once the host type (ha) is determined, remove candidate_host_types
        candidate.old_candidate_host_types = copy.deepcopy(candidate.candidate_host_types)
        candidate.candidate_host_types.clear()

        # Filter against host-aggregate, cpu, mem, disk, numa

        self.aggr_filter.init_condition()
        if self.aggr_filter.check_pre_condition(_level, _v, self.avail_hosts, self.avail_groups):
            if not self.aggr_filter._check_candidate(_level, _v, candidate):
                self.status = "host-aggregate violation"

        self.cpu_filter.init_condition()
        if not self.cpu_filter._check_candidate(_level, _v, candidate):
            self.status = "cpu violation"

        self.mem_filter.init_condition()
        if not self.mem_filter._check_candidate(_level, _v, candidate):
            self.status = "mem violation"

        self.disk_filter.init_condition()
        if not self.disk_filter._check_candidate(_level, _v, candidate):
            self.status = "disk violation"

        self.numa_filter.init_condition()
        if self.numa_filter.check_pre_condition(_level, _v, self.avail_hosts, self.avail_groups):
            if not self.numa_filter._check_candidate(_level, _v, candidate):
                self.status = "numa violation"

        if self.status is None:
            # Candidate not filtered.
            return [candidate]
        else:
            # Rollback
            candidate.rollback_avail_resources(ha)
            candidate.candidate_host_types = copy.deepcopy(candidate.old_candidate_host_types)
            candidate.old_candidate_host_types.clear()

            for hrk, hr in self.avail_hosts.iteritems():
                if hrk != candidate.host_name:
                    if hr.rack_name == candidate.rack_name:
                        hr.rollback_avail_rack_resources(ha,
                                                         candidate.rack_avail_vCPUs,
                                                         candidate.rack_avail_mem,
                                                         candidate.rack_avail_local_disk)

            return []
