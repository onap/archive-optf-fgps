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
from valet.engine.app_manager.server import Server


_SCOPE = 'hw'


class NUMAFilter(object):
    """Check NUMA alignment request in Flavor."""

    def __init__(self):
        """Define filter name and status."""

        self.name = "numa"

        self.status = None

    def init_condition(self):
        """Init variable."""

        self.status = None

    def check_pre_condition(self, _level, _v, _avail_hosts, _avail_groups):
        """Check if given server needs to check this filter."""

        if _level == "host" and isinstance(_v, Server):
            if _v.need_numa_alignment():
                return True

        return False

    def filter_candidates(self, _level, _v, _candidate_list):
        """Check and filter one candidate at a time."""

        candidate_list = []

        for c in _candidate_list:
            if self._check_candidate(_level, _v, c):
                candidate_list.append(c)

        return candidate_list

    def _check_candidate(self, _level, _v, _candidate):
        """Check given candidate host if it meets numa requirement."""

        # servers = []
        # if isinstance(_v, Group):
        #     _v.get_servers(servers)
        # else:
        #     servers.append(_v)

        # (vcpus_demand, mem_demand) = self._get_demand_with_numa(servers)

        return _candidate.NUMA.has_enough_resources(_v.vCPUs, _v.mem)

    def _get_demand_with_numa(self, _servers):
        """Check numa and compute the amount of vCPUs and memory."""

        vcpus = 0
        mem = 0

        for s in _servers:
            if s.need_numa_alignment():
                vcpus += s.vCPUs
                mem += s.mem

        return vcpus, mem
