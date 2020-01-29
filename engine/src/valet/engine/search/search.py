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
import operator

from valet.engine.app_manager.server import Server
from valet.engine.resource_manager.resources.datacenter import Datacenter
from valet.engine.search.avail_resources import AvailResources
from valet.engine.search.constraint_solver import ConstraintSolver
from valet.engine.search.resource import GroupResource, HostResource
from valet.engine.search.search_helper import *


class Search(object):
    """Bin-packing approach in the hierachical datacenter layout."""

    def __init__(self, _logger):
        self.logger = _logger

        # Search inputs
        self.app = None
        self.resource = None

        # Snapshot of current resource status
        self.avail_hosts = {}
        self.avail_groups = {}

        # Search results
        self.node_placements = {}
        self.prior_placements = {}    # TODO
        self.num_of_hosts = 0

        # Optimization criteria
        self.CPU_weight = -1
        self.mem_weight = -1
        self.local_disk_weight = -1

        self.constraint_solver = None

    def _init_search(self, _app):
        """Init the search information and the output results."""

        self.app = _app
        self.resource = _app.resource

        self.avail_hosts.clear()
        self.avail_groups.clear()

        self.node_placements.clear()
        self.prior_placements.clear()    # TODO
        self.num_of_hosts = 0

        self.CPU_weight = -1
        self.mem_weight = -1
        self.local_disk_weight = -1

        self.constraint_solver = ConstraintSolver(self.logger)

        self._create_avail_groups()
        self._create_avail_hosts()

        # TODO
        # if len(self.app.old_vm_map) > 0:
        #     self._adjust_resources()

        self._set_resource_weights()

    def _create_avail_groups(self):
        """Collect all available resource groups.

        Group type is affinity, diversity, quorum-diversity, exclusivity,
        availability-zone, host-aggregate, server-group.
        """

        for gk, g in self.resource.groups.items():
            if g.status != "enabled":
                self.logger.debug("group (" + g.name + ") disabled")
                continue

            gr = GroupResource()
            gr.name = gk

            gr.group_type = g.group_type
            gr.factory = g.factory

            if g.level is not None:
                gr.level = g.level
            else:
                gr.level = "host"

            for mk, mv in g.metadata.items():
                gr.metadata[mk] = mv

            gr.original_num_of_placed_servers = len(g.server_list)
            gr.num_of_placed_servers = len(g.server_list)

            for hk in g.member_hosts.keys():
                gr.num_of_placed_servers_of_host[hk] = len(g.member_hosts[hk])

            self.avail_groups[gk] = gr

    def _create_avail_hosts(self):
        """Create all available hosts."""

        for hk, host in self.resource.hosts.items():
            if not host.is_available():
                self.logger.warning("host (" + host.name + ") not available at this time")
                continue

            hr = HostResource()
            hr.host_name = hk

            for mk in host.memberships.keys():
                if mk in self.avail_groups.keys():
                    hr.host_memberships[mk] = self.avail_groups[mk]

            # Not used by Valet, only capacity planning
            try:
                for htk, ht in host.candidate_host_types.items():
                    hr.candidate_host_types[htk] = copy.deepcopy(ht)
            except AttributeError:
                hr.candidate_host_types = {}

            hr.host_avail_vCPUs = host.avail_vCPUs
            hr.host_avail_mem = host.avail_mem_cap
            hr.host_avail_local_disk = host.avail_local_disk_cap

            hr.NUMA = host.NUMA   # NOTE: refer to host's NUMA, instead of deepcopy.

            hr.host_num_of_placed_servers = len(host.server_list)

            rack = host.host_group
            if isinstance(rack, Datacenter):
                hr.rack_name = "any"
            else:
                if not rack.is_available():
                    continue

                hr.rack_name = rack.name

                for mk in rack.memberships.keys():
                    if mk in self.avail_groups.keys():
                        hr.rack_memberships[mk] = self.avail_groups[mk]

                hr.rack_avail_vCPUs = rack.avail_vCPUs
                hr.rack_avail_mem = rack.avail_mem_cap
                hr.rack_avail_local_disk = rack.avail_local_disk_cap

                hr.rack_num_of_placed_servers = len(rack.server_list)

            if hr.host_num_of_placed_servers > 0:
                self.num_of_hosts += 1

            self.avail_hosts[hk] = hr

    def _set_resource_weights(self):
        """Compute weight of each resource type.

           As larger weight, as more important resource to be considered.
        """

        denominator = 0.0
        for _, w in self.app.optimization_priority:
            denominator += w

        for t, w in self.app.optimization_priority:
            if t == "cpu":
                self.CPU_weight = float(w / denominator)
            elif t == "mem":
                self.mem_weight = float(w / denominator)
            elif t == "lvol":
                self.local_disk_weight = float(w / denominator)

    def place(self, _app):
        """Determine placements of new app creation."""

        self._init_search(_app)

        self.logger.info("search......")

        open_node_list = self._open_list(self.app.servers, self.app.groups)

        avail_resources = AvailResources(LEVEL[len(LEVEL) - 1])
        avail_resources.avail_hosts = self.avail_hosts
        avail_resources.set_next_level()   # NOTE(Gueyoung): skip 'cluster' level

        return self._run_greedy(open_node_list, avail_resources, "new")

    # TODO: for update opt.
    def re_place(self, _app_topology):
        pass

    def _re_place(self):
        pass

    def _open_list(self, _servers, _groups):
        """Extract all servers and groups of each level (rack, host)."""

        open_node_list = []

        for _, s in _servers.items():
            self._set_node_weight(s)
            open_node_list.append(s)

        for _, g in _groups.items():
            self._set_node_weight(g)
            open_node_list.append(g)

        return open_node_list

    def _set_node_weight(self, _v):
        """Compute each server's or group's weight.

           As larger weight, as more important one to be considered.
        """

        _v.sort_base = -1
        _v.sort_base = self.CPU_weight * _v.vCPU_weight
        _v.sort_base += self.mem_weight * _v.mem_weight
        _v.sort_base += self.local_disk_weight * _v.local_volume_weight

    # TODO: for update opt.
    def _open_prior_list(self, _vms, _groups):
        pass

    def _adjust_resources(self):
        pass

    def _run_greedy(self, _open_node_list, _avail_resources, _mode):
        """Search placements with greedy algorithm."""

        _open_node_list.sort(key=operator.attrgetter("sort_base"), reverse=True)

        for n in _open_node_list:
            self.logger.debug("open node = " + n.vid + " cpus = " + str(n.vCPUs) + " sort = " + str(n.sort_base))

        while len(_open_node_list) > 0:
            n = _open_node_list.pop(0)

            # TODO
            # if _mode == "new":
            best_resource = self._get_best_resource(n, _avail_resources, _mode)
            # else:
            #     best_resource = self._get_best_resource_for_prior(n, _avail_resources, _mode)

            if best_resource is None:
                self.logger.error(self.app.status)
                return False
            else:
                self._deduct_resources(_avail_resources.level, best_resource, n, _mode)
                # TODO
                # if _mode == "new":
                self._close_node_placement(_avail_resources.level, best_resource, n)
                # else:
                #     self._close_prior_placement(_avail_resources.level, best_resource, n)

        return True

    def _get_best_resource(self, _n, _avail_resources, _mode):
        """Ddetermine the best placement for given server or affinity group."""

        candidate_list = []
        prior_resource = None

        # If this is already placed one
        if _n in self.prior_placements.keys():
            prior_resource = _avail_resources.get_candidate(self.prior_placements[_n])
            candidate_list.append(prior_resource)
        else:
            # TODO: need a list of candidates given as input?

            _avail_resources.set_candidates()

            candidate_list = self.constraint_solver.get_candidate_list(_n,
                                                                       _avail_resources,
                                                                       self.avail_hosts,
                                                                       self.avail_groups)

        if len(candidate_list) == 0:
            if self.app.status == "ok":
                if self.constraint_solver.status != "ok":
                    self.app.status = self.constraint_solver.status
                else:
                    self.app.status = "fail while getting candidate hosts"
            return None

        if len(candidate_list) > 1:
            self._set_compute_sort_base(_avail_resources.level, candidate_list)
            candidate_list.sort(key=operator.attrgetter("sort_base"))

        for c in candidate_list:
            rn = c.get_resource_name(_avail_resources.level)
            avail_cpus = c.get_vcpus(_avail_resources.level)
            self.logger.debug("candidate = " + rn + " cpus = " + str(avail_cpus) + " sort = " + str(c.sort_base))

        best_resource = None
        if _avail_resources.level == "host" and isinstance(_n, Server):
            best_resource = copy.deepcopy(candidate_list[0])
            best_resource.level = "host"
        else:
            while len(candidate_list) > 0:
                cr = candidate_list.pop(0)

                (servers, groups) = get_next_placements(_n, _avail_resources.level)
                open_node_list = self._open_list(servers, groups)

                avail_resources = AvailResources(_avail_resources.level)
                resource_name = cr.get_resource_name(_avail_resources.level)

                avail_resources.set_next_avail_hosts(_avail_resources.avail_hosts, resource_name)
                avail_resources.set_next_level()

                # Recursive call
                if self._run_greedy(open_node_list, avail_resources, _mode):
                    best_resource = copy.deepcopy(cr)
                    best_resource.level = _avail_resources.level
                    break
                else:
                    if prior_resource is None:
                        self.logger.warning("rollback candidate = " + resource_name)

                        self._rollback_resources(_n)
                        self._rollback_node_placement(_n)

                        # TODO(Gueyoung): how to track the original error status?
                        if len(candidate_list) > 0 and self.app.status != "ok":
                            self.app.status = "ok"
                    else:
                        break

        if best_resource is None and len(candidate_list) == 0:
            if self.app.status == "ok":
                self.app.status = "no available hosts"
            self.logger.warning(self.app.status)

        return best_resource

    # TODO: for update opt.
    def _get_best_resource_for_prior(self, _n, _avail_resources, _mode):
        pass

    def _set_compute_sort_base(self, _level, _candidate_list):
        """Compute the weight of each candidate host."""

        for c in _candidate_list:
            cpu_ratio = -1
            mem_ratio = -1
            local_disk_ratio = -1

            if _level == "rack":
                cpu_ratio = float(c.rack_avail_vCPUs) / float(self.resource.CPU_avail)
                mem_ratio = float(c.rack_avail_mem) / float(self.resource.mem_avail)
                local_disk_ratio = float(c.rack_avail_local_disk) / float(self.resource.local_disk_avail)
            elif _level == "host":
                cpu_ratio = float(c.host_avail_vCPUs) / float(self.resource.CPU_avail)
                mem_ratio = float(c.host_avail_mem) / float(self.resource.mem_avail)
                local_disk_ratio = float(c.host_avail_local_disk) / float(self.resource.local_disk_avail)

            c.sort_base = (1.0 - self.CPU_weight) * cpu_ratio + \
                          (1.0 - self.mem_weight) * mem_ratio + \
                          (1.0 - self.local_disk_weight) * local_disk_ratio

    def _deduct_resources(self, _level, _best, _n, _mode):
        """Apply new placement to hosting resources and groups."""

        # Check if the chosen host is already applied.
        if _mode == "new":
            if _n in self.prior_placements.keys():
                return
            else:
                if _n in self.node_placements.keys():
                    if _best.level == self.node_placements[_n].level:
                        return
        else:
            if _n in self.prior_placements.keys():
                if _best.level == self.prior_placements[_n].level:
                    return

        # Apply this placement to valet groups.

        exclusivities = _n.get_exclusivities(_level)
        if len(exclusivities) == 1:
            exclusivity_group = exclusivities[exclusivities.keys()[0]]
            self._add_exclusivity(_best, exclusivity_group)

        if isinstance(_n, Group):
            self._add_group(_level, _best, _n)

        if len(_n.diversity_groups) > 0:
            for _, div_group in _n.diversity_groups.items():
                self._add_group(_level, _best, div_group)

        if len(_n.quorum_diversity_groups) > 0:
            for _, div_group in _n.quorum_diversity_groups.items():
                self._add_group(_level, _best, div_group)

        # Apply this placement to hosting resources.
        if isinstance(_n, Server) and _level == "host":
            self._deduct_server_resources(_best, _n)

    def _add_exclusivity(self, _best, _group):
        """Add new exclusivity group."""

        if _group.vid not in self.avail_groups.keys():
            gr = GroupResource()
            gr.name = _group.vid
            gr.group_type = "exclusivity"
            gr.factory = "valet"
            gr.level = _group.level
            self.avail_groups[gr.name] = gr

            self.logger.info("find exclusivity (" + _group.vid + ")")
        else:
            gr = self.avail_groups[_group.vid]

        gr.num_of_placed_servers += 1

        host_name = _best.get_resource_name(_group.level)
        if host_name not in gr.num_of_placed_servers_of_host.keys():
            gr.num_of_placed_servers_of_host[host_name] = 0
        gr.num_of_placed_servers_of_host[host_name] += 1

        chosen_host = self.avail_hosts[_best.host_name]
        if _group.level == "host":
            if _group.vid not in chosen_host.host_memberships.keys():
                chosen_host.host_memberships[_group.vid] = gr
            for _, np in self.avail_hosts.items():
                if chosen_host.rack_name != "any" and np.rack_name == chosen_host.rack_name:
                    if _group.vid not in np.rack_memberships.keys():
                        np.rack_memberships[_group.vid] = gr
        else:    # Rack level
            for _, np in self.avail_hosts.items():
                if chosen_host.rack_name != "any" and np.rack_name == chosen_host.rack_name:
                    if _group.vid not in np.rack_memberships.keys():
                        np.rack_memberships[_group.vid] = gr

    def _add_group(self, _level, _best, _group):
        """Add new valet group."""

        if _group.vid not in self.avail_groups.keys():
            gr = GroupResource()
            gr.name = _group.vid
            gr.group_type = _group.group_type
            gr.factory = _group.factory
            gr.level = _group.level
            self.avail_groups[gr.name] = gr

            self.logger.info("find " + _group.group_type + " (" + _group.vid + ")")
        else:
            gr = self.avail_groups[_group.vid]

        if _group.level == _level:
            gr.num_of_placed_servers += 1

            host_name = _best.get_resource_name(_level)
            if host_name not in gr.num_of_placed_servers_of_host.keys():
                gr.num_of_placed_servers_of_host[host_name] = 0
            gr.num_of_placed_servers_of_host[host_name] += 1

            chosen_host = self.avail_hosts[_best.host_name]
            if _level == "host":
                if _group.vid not in chosen_host.host_memberships.keys():
                    chosen_host.host_memberships[_group.vid] = gr
                for _, np in self.avail_hosts.items():
                    if chosen_host.rack_name != "any" and np.rack_name == chosen_host.rack_name:
                        if _group.vid not in np.rack_memberships.keys():
                            np.rack_memberships[_group.vid] = gr
            else:    # Rack level
                for _, np in self.avail_hosts.items():
                    if chosen_host.rack_name != "any" and np.rack_name == chosen_host.rack_name:
                        if _group.vid not in np.rack_memberships.keys():
                            np.rack_memberships[_group.vid] = gr

    def _deduct_server_resources(self, _best, _n):
        """Apply the reduced amount of resources to the chosen host.

        _n is a server and _best is a compute host.
        """

        chosen_host = self.avail_hosts[_best.host_name]

        chosen_host.host_avail_vCPUs -= _n.vCPUs
        chosen_host.host_avail_mem -= _n.mem
        chosen_host.host_avail_local_disk -= _n.local_volume_size

        # Apply placement decision into NUMA
        if _n.need_numa_alignment():
            s_info = {}
            s_info["stack_id"] = "none"
            s_info["stack_name"] = self.app.app_name
            s_info["uuid"] = "none"
            s_info["name"] = _n.name
            s_info["vcpus"] = _n.vCPUs
            s_info["mem"] = _n.mem

            chosen_host.NUMA.deduct_server_resources(s_info)

        # TODO: need non_NUMA server?
        # else:
        #     chosen_host.NUMA.apply_cpus_fairly(_n.vCPUs)
        #     chosen_host.NUMA.apply_mem_fairly(_n.mem)

        if chosen_host.host_num_of_placed_servers == 0:
            self.num_of_hosts += 1

        chosen_host.host_num_of_placed_servers += 1

        for _, np in self.avail_hosts.items():
            if chosen_host.rack_name != "any" and np.rack_name == chosen_host.rack_name:
                np.rack_avail_vCPUs -= _n.vCPUs
                np.rack_avail_mem -= _n.mem
                np.rack_avail_local_disk -= _n.local_volume_size

                np.rack_num_of_placed_servers += 1

    def _close_node_placement(self, _level, _best, _v):
        """Record the final placement decision."""

        if _v not in self.node_placements.keys() and _v not in self.prior_placements.keys():
            if _level == "host" or isinstance(_v, Group):
                self.node_placements[_v] = _best

    def _close_prior_placement(self, _level, _best, _v):
        """Set the decision for placed server or group."""

        if _v not in self.prior_placements.keys():
            if _level == "host" or isinstance(_v, Group):
                self.prior_placements[_v] = _best

    def _rollback_resources(self, _v):
        """Rollback the placement."""

        if isinstance(_v, Server):
            self._rollback_server_resources(_v)
        elif isinstance(_v, Group):
            for _, v in _v.subgroups.items():
                self._rollback_resources(v)

        if _v in self.node_placements.keys():
            chosen_host = self.avail_hosts[self.node_placements[_v].host_name]
            level = self.node_placements[_v].level

            if isinstance(_v, Group):
                self._remove_group(chosen_host, _v, level)

            exclusivities = _v.get_exclusivities(level)
            if len(exclusivities) == 1:
                ex_group = exclusivities[exclusivities.keys()[0]]
                self._remove_exclusivity(chosen_host, ex_group)

            if len(_v.diversity_groups) > 0:
                for _, div_group in _v.diversity_groups.items():
                    self._remove_group(chosen_host, div_group, level)

            if len(_v.quorum_diversity_groups) > 0:
                for _, div_group in _v.quorum_diversity_groups.items():
                    self._remove_group(chosen_host, div_group, level)

    def _remove_exclusivity(self, _chosen_host, _group):
        """Remove the exclusivity group."""

        gr = self.avail_groups[_group.vid]

        host_name = _chosen_host.get_resource_name(_group.level)

        gr.num_of_placed_servers -= 1
        gr.num_of_placed_servers_of_host[host_name] -= 1

        if gr.num_of_placed_servers_of_host[host_name] == 0:
            del gr.num_of_placed_servers_of_host[host_name]

        if gr.num_of_placed_servers == 0:
            del self.avail_groups[_group.vid]

        if _group.level == "host":
            if _chosen_host.host_num_of_placed_servers == 0 and \
               _group.vid in _chosen_host.host_memberships.keys():
                del _chosen_host.host_memberships[_group.vid]

                for _, np in self.avail_hosts.items():
                    if _chosen_host.rack_name != "any" and np.rack_name == _chosen_host.rack_name:
                        if _group.vid in np.rack_memberships.keys():
                            del np.rack_memberships[_group.vid]
        else:    # Rack level
            if _chosen_host.rack_num_of_placed_servers == 0:
                for _, np in self.avail_hosts.items():
                    if _chosen_host.rack_name != "any" and np.rack_name == _chosen_host.rack_name:
                        if _group.vid in np.rack_memberships.keys():
                            del np.rack_memberships[_group.vid]

    def _remove_group(self, _chosen_host, _group, _level):
        """Remove valet group."""

        if _group.level == _level:
            gr = self.avail_groups[_group.vid]

            host_name = _chosen_host.get_resource_name(_level)

            gr.num_of_placed_servers -= 1
            gr.num_of_placed_servers_of_host[host_name] -= 1

            if gr.num_of_placed_servers_of_host[host_name] == 0:
                del gr.num_of_placed_servers_of_host[host_name]

            if gr.num_of_placed_servers == 0:
                del self.avail_groups[_group.vid]

            exist_group = True
            if _group.vid not in self.avail_groups.keys():
                exist_group = False
            else:
                if host_name not in gr.num_of_placed_servers_of_host.keys():
                    exist_group = False

            if _level == "host":
                if not exist_group and _group.vid in _chosen_host.host_memberships.keys():
                    del _chosen_host.host_memberships[_group.vid]

                    for _, np in self.avail_hosts.items():
                        if _chosen_host.rack_name != "any" and np.rack_name == _chosen_host.rack_name:
                            if _group.vid in np.rack_memberships.keys():
                                del np.rack_memberships[_group.vid]
            else:    # Rack level
                if not exist_group:
                    for _, np in self.avail_hosts.items():
                        if _chosen_host.rack_name != "any" and np.rack_name == _chosen_host.rack_name:
                            if _group.vid in np.rack_memberships.keys():
                                del np.rack_memberships[_group.vid]

    def _rollback_server_resources(self, _v):
        """Return back the amount of resources to host."""

        if _v in self.node_placements.keys():
            chosen_host = self.avail_hosts[self.node_placements[_v].host_name]

            chosen_host.host_avail_vCPUs += _v.vCPUs
            chosen_host.host_avail_mem += _v.mem
            chosen_host.host_avail_local_disk += _v.local_volume_size

            # Apply rollback into NUMA
            if _v.need_numa_alignment():
                s_info = {}
                s_info["stack_id"] = "none"
                s_info["stack_name"] = self.app.app_name
                s_info["uuid"] = "none"
                s_info["name"] = _v.name
                s_info["vcpus"] = _v.vCPUs
                s_info["mem"] = _v.mem

                chosen_host.NUMA.rollback_server_resources(s_info)

            chosen_host.host_num_of_placed_servers -= 1

            if chosen_host.host_num_of_placed_servers == 0:
                self.num_of_hosts -= 1

            for _, np in self.avail_hosts.items():
                if chosen_host.rack_name != "any" and np.rack_name == chosen_host.rack_name:
                    np.rack_avail_vCPUs += _v.vCPUs
                    np.rack_avail_mem += _v.mem
                    np.rack_avail_local_disk += _v.local_volume_size

                    np.rack_num_of_placed_servers -= 1

            # If the chosen host was a new host and its host type was unknown,
            # rollback to the original unknown state.
            if chosen_host.host_num_of_placed_servers == 0:
                if chosen_host.old_candidate_host_types is not None and len(chosen_host.old_candidate_host_types) > 0:
                    flavor_type_list = _v.get_flavor_types()
                    ha = self.avail_groups[flavor_type_list[0]]

                    chosen_host.rollback_avail_resources(ha)
                    chosen_host.candidate_host_types = copy.deepcopy(chosen_host.old_candidate_host_types)
                    chosen_host.old_candidate_host_types.clear()

                    for hrk, hr in self.avail_hosts.items():
                        if hrk != chosen_host.host_name:
                            if hr.rack_name == chosen_host.rack_name:
                                hr.rollback_avail_rack_resources(ha,
                                                                 chosen_host.rack_avail_vCPUs,
                                                                 chosen_host.rack_avail_mem,
                                                                 chosen_host.rack_avail_local_disk)

    def _rollback_node_placement(self, _v):
        """Remove placement decisions."""

        if _v in self.node_placements.keys():
            del self.node_placements[_v]

        if isinstance(_v, Group):
            for _, sg in _v.subgroups.items():
                self._rollback_node_placement(sg)
