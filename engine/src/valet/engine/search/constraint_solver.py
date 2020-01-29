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
from valet.engine.search.filters.affinity_filter import AffinityFilter
from valet.engine.search.filters.aggregate_instance_filter import AggregateInstanceExtraSpecsFilter
from valet.engine.search.filters.az_filter import AvailabilityZoneFilter
from valet.engine.search.filters.cpu_filter import CPUFilter
from valet.engine.search.filters.disk_filter import DiskFilter
from valet.engine.search.filters.diversity_filter import DiversityFilter
from valet.engine.search.filters.dynamic_aggregate_filter import DynamicAggregateFilter
from valet.engine.search.filters.exclusivity_filter import ExclusivityFilter
from valet.engine.search.filters.mem_filter import MemFilter
from valet.engine.search.filters.no_exclusivity_filter import NoExclusivityFilter
from valet.engine.search.filters.numa_filter import NUMAFilter
from valet.engine.search.filters.quorum_diversity_filter import QuorumDiversityFilter


class ConstraintSolver(object):
    """Constraint solver to filter out candidate hosts."""

    def __init__(self, _logger):
        """Define fileters and application order."""

        self.logger = _logger

        self.filter_list = []

        # TODO(Gueyoung): add soft-affinity and soft-diversity filters

        # TODO(Gueyoung): the order of applying filters?

        # Apply platform filters first
        self.filter_list.append(AvailabilityZoneFilter())
        self.filter_list.append(AggregateInstanceExtraSpecsFilter())
        self.filter_list.append(CPUFilter())
        self.filter_list.append(MemFilter())
        self.filter_list.append(DiskFilter())
        self.filter_list.append(NUMAFilter())

        # Apply Valet filters next
        self.filter_list.append(DiversityFilter())
        self.filter_list.append(QuorumDiversityFilter())
        self.filter_list.append(ExclusivityFilter())
        self.filter_list.append(NoExclusivityFilter())
        self.filter_list.append(AffinityFilter())

        # Apply dynamic aggregate filter to determine the host's aggregate
        # in a lazy way.
        self.filter_list.append(DynamicAggregateFilter())

        self.status = "ok"

    def get_candidate_list(self, _n, _avail_resources, _avail_hosts, _avail_groups):
        """Filter candidate hosts using a list of filters."""

        level = _avail_resources.level

        candidate_list = []

        # This is the resource which name is 'any'
        ghost_candidate = None

        for _, r in _avail_resources.candidates.items():
            candidate_list.append(r)

            if r.get_resource_name(level) == "any":
                ghost_candidate = r

        if len(candidate_list) == 0:
            self.status = "no candidate for node = " + _n.vid
            self.logger.warning(self.status)
            return []

        for f in self.filter_list:
            f.init_condition()

            if not f.check_pre_condition(level, _n, _avail_hosts, _avail_groups):
                if f.status is not None:
                    self.status = f.status
                    self.logger.error(self.status)
                    return []
                else:
                    self.logger.debug("skip " + f.name + " constraint for node = " + _n.vid)

                continue

            candidate_list = f.filter_candidates(level, _n, candidate_list)

            if ghost_candidate and ghost_candidate not in candidate_list:
                candidate_list.append(ghost_candidate)

            if len(candidate_list) == 0:
                self.status = "violate " + level + " " + f.name + " constraint for node = " + _n.vid
                if f.status is not None:
                    self.status += " detail: " + f.status
                self.logger.debug(self.status)
                return []
            elif len(candidate_list) > 0:
                str_num = str(len(candidate_list))
                self.logger.debug("pass " + f.name + " constraint for node = " + _n.vid + " with " + str_num)

        return candidate_list
