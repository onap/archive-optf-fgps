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
import six
import time

from valet.engine.app_manager.group import LEVEL
from valet.engine.resource_manager.resources.datacenter import Datacenter
from valet.engine.resource_manager.resources.flavor import Flavor
from valet.engine.resource_manager.resources.group import Group
from valet.engine.resource_manager.resources.host import Host
from valet.engine.resource_manager.resources.host_group import HostGroup
from valet.engine.resource_manager.resources.numa import NUMA


class Resource(object):
    """Container for resource status of a datacenter and all metadata."""

    def __init__(self, _datacenter, _dbh, _compute, _metadata, _topology, _logger):
        self.dbh = _dbh

        self.compute = _compute
        self.metadata = _metadata
        self.topology = _topology

        self.group_rules = {}

        self.datacenter = None
        self.datacenter_id = _datacenter.get("id")
        self.datacenter_url = _datacenter.get("url", "none")

        self.host_groups = {}
        self.hosts = {}

        self.change_of_placements = {}

        self.groups = {}
        self.flavors = {}

        self.CPU_avail = 0
        self.mem_avail = 0
        self.local_disk_avail = 0

        self.default_cpu_allocation_ratio = 1.0
        self.default_ram_allocation_ratio = 1.0
        self.default_disk_allocation_ratio = 1.0

        self.new = False

        # To keep unconfirmed requests.
        # If exist, do NOT sync with platform for the next request.
        self.pending_requests = []

        self.logger = _logger

    def set_config(self, _cpu_ratio, _ram_ratio, _disk_ratio):
        self.default_cpu_allocation_ratio = _cpu_ratio
        self.default_ram_allocation_ratio = _ram_ratio
        self.default_disk_allocation_ratio = _disk_ratio

    def set_group_rules(self, _rules):
        self.group_rules = _rules

    def load_resource_from_db(self):
        """Load datacenter's resource info from DB.

        Note: all resources in DB are enabled ones.
        """

        self.logger.info("load datacenter resource info from DB")

        # Load Valet groups first.
        valet_group_list = self.dbh.get_valet_groups()
        if valet_group_list is None:
            return None

        valet_groups = {}
        for vg in valet_group_list:
            vgk = vg.get("id")
            dc_id = vgk.split(':', 1)

            if dc_id[0] == self.datacenter_id:
                if vg["rule_id"] in self.group_rules.keys():
                    vg["metadata"] = json.loads(vg["metadata"])
                    vg["server_list"] = json.loads(vg["server_list"])
                    vg["member_hosts"] = json.loads(vg["member_hosts"])
                    vg["group_type"] = vg["type"]

                    valet_groups[vgk] = vg

        self._load_groups(valet_groups)

        dcr = self.dbh.get_resource(self.datacenter_id)
        if dcr is None:
            return None

        if len(dcr) == 0:
            return "no resource found for datacenter = " + self.datacenter_id

        if self.datacenter_url == "none":
            self.datacenter_url = dcr["url"]

        pending_requests = json.loads(dcr["requests"])
        for req in pending_requests:
            self.pending_requests.append(req)

        resource = json.loads(dcr["resource"])

        groups = resource.get("groups")
        if groups:
            self._load_groups(groups)

        flavors = resource.get("flavors")
        if flavors:
            self._load_flavors(flavors)

        if len(self.flavors) == 0:
            self.logger.warning("no flavors in db record")

        hosts = resource.get("hosts")
        if hosts:
            self._load_hosts(hosts)

        if len(self.hosts) == 0:
            self.logger.warning("no hosts in db record")

        host_groups = resource.get("host_groups")
        if host_groups:
            self._load_host_groups(host_groups)

        if len(self.host_groups) == 0:
            self.logger.warning("no host_groups (rack)")

        dc = resource.get("datacenter")
        self._load_datacenter(dc)

        for ck in dc.get("children"):
            if ck in self.host_groups.keys():
                self.datacenter.resources[ck] = self.host_groups[ck]
            elif ck in self.hosts.keys():
                self.datacenter.resources[ck] = self.hosts[ck]

        hgs = resource.get("host_groups")
        if hgs:
            for hgk, hg in hgs.items():
                host_group = self.host_groups[hgk]

                pk = hg.get("parent")
                if pk == self.datacenter.name:
                    host_group.parent_resource = self.datacenter
                elif pk in self.host_groups.keys():
                    host_group.parent_resource = self.host_groups[pk]

                for ck in hg.get("children"):
                    if ck in self.hosts.keys():
                        host_group.child_resources[ck] = self.hosts[ck]
                    elif ck in self.host_groups.keys():
                        host_group.child_resources[ck] = self.host_groups[ck]

        hs = resource.get("hosts")
        if hs:
            for hk, h in hs.items():
                host = self.hosts[hk]

                pk = h.get("parent")
                if pk == self.datacenter.name:
                    host.host_group = self.datacenter
                elif pk in self.host_groups.keys():
                    host.host_group = self.host_groups[pk]

        for _, g in self.groups.items():
            for hk in g.member_hosts.keys():
                if hk not in self.hosts.keys() and \
                   hk not in self.host_groups.keys():
                    del g.member_hosts[hk]

        self._update_compute_avail()

        return "ok"

    def _load_groups(self, _groups):
        """Take JSON group data as defined in /resources/group and
           create Group instance.
        """

        for gk, g in _groups.items():
            group = Group(gk)

            group.status = g.get("status")

            group.uuid = g.get("uuid")

            group.group_type = g.get("group_type")
            group.level = g.get("level")
            group.factory = g.get("factory")

            rule_id = g.get("rule_id")
            if rule_id != "none" and rule_id in self.group_rules.keys():
                group.rule = self.group_rules[rule_id]

            for mk, mv in g["metadata"].items():
                group.metadata[mk] = mv

            for s_info in g["server_list"]:
                group.server_list.append(s_info)

            for hk, server_list in g["member_hosts"].items():
                group.member_hosts[hk] = []
                for s_info in server_list:
                    group.member_hosts[hk].append(s_info)

            self.groups[gk] = group

    def _load_flavors(self, _flavors):
        """Take JSON flavor data as defined in /resources/flavor and
           create Flavor instance.
        """

        for fk, f in _flavors.items():
            flavor = Flavor(fk)

            flavor.status = f.get("status")

            flavor.flavor_id = f.get("flavor_id")
            flavor.vCPUs = f.get("vCPUs")
            flavor.mem_cap = f.get("mem")
            flavor.disk_cap = f.get("disk")
            for k, v in f["extra_specs"].items():
                flavor.extra_specs[k] = v

            self.flavors[fk] = flavor

    def _load_hosts(self, _hosts):
        """Take JSON host data as defined in /resources/host and
           create Host instance.
        """

        for hk, h in _hosts.items():
            host = Host(hk)

            host.status = h.get("status")
            host.state = h.get("state")

            host.uuid = h.get("uuid")

            host.vCPUs = h.get("vCPUs")
            host.original_vCPUs = h.get("original_vCPUs")
            host.vCPUs_used = h.get("vCPUs_used")
            host.avail_vCPUs = h.get("avail_vCPUs")

            host.mem_cap = h.get("mem")
            host.original_mem_cap = h.get("original_mem")
            host.free_mem_mb = h.get("free_mem_mb")
            host.avail_mem_cap = h.get("avail_mem")

            host.local_disk_cap = h.get("local_disk")
            host.original_local_disk_cap = h.get("original_local_disk")
            host.free_disk_gb = h.get("free_disk_gb")
            host.disk_available_least = h.get("disk_available_least")
            host.avail_local_disk_cap = h.get("avail_local_disk")

            host.NUMA = NUMA(numa=h.get("NUMA"))

            for s_info in h["server_list"]:
                host.server_list.append(s_info)

            for gk in h["membership_list"]:
                if gk in self.groups.keys():
                    host.memberships[gk] = self.groups[gk]

            # Not used by Valet currently, only capacity planning module
            if "candidate_host_types" in h.keys():
                for htk, ht in h["candidate_host_types"].items():
                    host.candidate_host_types[htk] = ht
            else:
                host.candidate_host_types = {}

            self.hosts[hk] = host

    def _load_host_groups(self, _host_groups):
        for hgk, hg in _host_groups.items():
            host_group = HostGroup(hgk)

            host_group.status = hg.get("status")

            host_group.host_type = hg.get("host_type")

            host_group.vCPUs = hg.get("vCPUs")
            host_group.avail_vCPUs = hg.get("avail_vCPUs")

            host_group.mem_cap = hg.get("mem")
            host_group.avail_mem_cap = hg.get("avail_mem")

            host_group.local_disk_cap = hg.get("local_disk")
            host_group.avail_local_disk_cap = hg.get("avail_local_disk")

            for s_info in hg["server_list"]:
                host_group.server_list.append(s_info)

            for gk in hg.get("membership_list"):
                if gk in self.groups.keys():
                    host_group.memberships[gk] = self.groups[gk]

            self.host_groups[hgk] = host_group

    def _load_datacenter(self, _dc):
        self.datacenter = Datacenter(_dc.get("name"))

        self.datacenter.status = _dc.get("status")

        self.datacenter.vCPUs = _dc.get("vCPUs")
        self.datacenter.avail_vCPUs = _dc.get("avail_vCPUs")

        self.datacenter.mem_cap = _dc.get("mem")
        self.datacenter.avail_mem_cap = _dc.get("avail_mem")

        self.datacenter.local_disk_cap = _dc.get("local_disk")
        self.datacenter.avail_local_disk_cap = _dc.get("avail_local_disk")

        for s_info in _dc["server_list"]:
            self.datacenter.server_list.append(s_info)

        for gk in _dc.get("membership_list"):
            if gk in self.groups.keys():
                self.datacenter.memberships[gk] = self.groups[gk]

    def _update_compute_avail(self):
        """Update amount of total available resources."""

        self.CPU_avail = self.datacenter.avail_vCPUs
        self.mem_avail = self.datacenter.avail_mem_cap
        self.local_disk_avail = self.datacenter.avail_local_disk_cap

    def update_resource(self):
        """Update resource status triggered by placements, events, and batch."""

        for level in LEVEL:
            for _, host_group in self.host_groups.items():
                if host_group.host_type == level:
                    if host_group.is_available() and host_group.updated:
                        self._update_host_group(host_group)

        if self.datacenter.updated:
            self._update_datacenter()

        self._update_compute_avail()

    def _update_host_group(self, _host_group):
        """Update host group (rack) status."""

        _host_group.init_resources()
        del _host_group.server_list[:]
        _host_group.init_memberships()

        for _, host in _host_group.child_resources.items():
            if host.is_available():
                _host_group.vCPUs += host.vCPUs
                _host_group.avail_vCPUs += host.avail_vCPUs
                _host_group.mem_cap += host.mem_cap
                _host_group.avail_mem_cap += host.avail_mem_cap
                _host_group.local_disk_cap += host.local_disk_cap
                _host_group.avail_local_disk_cap += host.avail_local_disk_cap

                for server_info in host.server_list:
                    _host_group.server_list.append(server_info)

                for gk in host.memberships.keys():
                    _host_group.memberships[gk] = host.memberships[gk]

    def _update_datacenter(self):
        """Update datacenter status."""

        self.datacenter.init_resources()
        del self.datacenter.server_list[:]
        self.datacenter.memberships.clear()

        for _, resource in self.datacenter.resources.items():
            if resource.is_available():
                self.datacenter.vCPUs += resource.vCPUs
                self.datacenter.avail_vCPUs += resource.avail_vCPUs
                self.datacenter.mem_cap += resource.mem_cap
                self.datacenter.avail_mem_cap += resource.avail_mem_cap
                self.datacenter.local_disk_cap += resource.local_disk_cap
                self.datacenter.avail_local_disk_cap += resource.avail_local_disk_cap

                for s in resource.server_list:
                    self.datacenter.server_list.append(s)

                for gk in resource.memberships.keys():
                    self.datacenter.memberships[gk] = resource.memberships[gk]

    def compute_resources(self, host):
        """Compute the amount of resources with oversubsription ratios."""

        ram_allocation_ratio_list = []
        cpu_allocation_ratio_list = []
        disk_allocation_ratio_list = []

        for _, g in host.memberships.items():
            if g.group_type == "aggr":
                if g.name.startswith("valet:"):
                    metadata = g.metadata["prior_metadata"]
                else:
                    metadata = g.metadata

                if "ram_allocation_ratio" in metadata.keys():
                    if isinstance(metadata["ram_allocation_ratio"], list):
                        for r in metadata["ram_allocation_ratio"]:
                            ram_allocation_ratio_list.append(float(r))
                    else:
                        ram_allocation_ratio_list.append(float(metadata["ram_allocation_ratio"]))
                if "cpu_allocation_ratio" in metadata.keys():
                    if isinstance(metadata["cpu_allocation_ratio"], list):
                        for r in metadata["cpu_allocation_ratio"]:
                            cpu_allocation_ratio_list.append(float(r))
                    else:
                        cpu_allocation_ratio_list.append(float(metadata["cpu_allocation_ratio"]))
                if "disk_allocation_ratio" in metadata.keys():
                    if isinstance(metadata["disk_allocation_ratio"], list):
                        for r in metadata["disk_allocation_ratio"]:
                            disk_allocation_ratio_list.append(float(r))
                    else:
                        disk_allocation_ratio_list.append(float(metadata["disk_allocation_ratio"]))

        ram_allocation_ratio = 1.0
        if len(ram_allocation_ratio_list) > 0:
            ram_allocation_ratio = min(ram_allocation_ratio_list)
        else:
            if self.default_ram_allocation_ratio > 0:
                ram_allocation_ratio = self.default_ram_allocation_ratio

        host.compute_mem(ram_allocation_ratio)

        cpu_allocation_ratio = 1.0
        if len(cpu_allocation_ratio_list) > 0:
            cpu_allocation_ratio = min(cpu_allocation_ratio_list)
        else:
            if self.default_cpu_allocation_ratio > 0:
                cpu_allocation_ratio = self.default_cpu_allocation_ratio

        host.compute_cpus(cpu_allocation_ratio)

        disk_allocation_ratio = 1.0
        if len(disk_allocation_ratio_list) > 0:
            disk_allocation_ratio = min(disk_allocation_ratio_list)
        else:
            if self.default_disk_allocation_ratio > 0:
                disk_allocation_ratio = self.default_disk_allocation_ratio

        host.compute_disk(disk_allocation_ratio)

    def compute_avail_resources(self, host):
        """Compute available amount of resources after placements."""

        status = host.compute_avail_mem()
        if status != "ok":
            self.logger.warning(status)

        status = host.compute_avail_cpus()
        if status != "ok":
            self.logger.warning(status)

        status = host.compute_avail_disk()
        if status != "ok":
            self.logger.warning(status)

    def mark_host_updated(self, _host_name):
        """Mark the host updated."""

        host = self.hosts[_host_name]
        host.updated = True

        if host.host_group is not None:
            if isinstance(host.host_group, HostGroup):
                self.mark_host_group_updated(host.host_group.name)
            else:
                self.mark_datacenter_updated()

    def mark_host_group_updated(self, _name):
        """Mark the host_group updated."""

        host_group = self.host_groups[_name]
        host_group.updated = True

        if host_group.parent_resource is not None:
            if isinstance(host_group.parent_resource, HostGroup):
                self.mark_host_group_updated(host_group.parent_resource.name)
            else:
                self.mark_datacenter_updated()

    def mark_datacenter_updated(self):
        """Mark the datacenter updated."""

        if self.datacenter is not None:
            self.datacenter.updated = True

    def get_host_of_server(self, _s_info):
        """Check and return host that hosts this server."""

        host = None

        if len(self.change_of_placements) > 0:
            if _s_info["stack_id"] != "none":
                sid = _s_info["stack_id"] + ":" + _s_info["name"]
            else:
                sid = _s_info["uuid"]

            if sid in self.change_of_placements.keys():
                host_name = None
                if "host" in self.change_of_placements[sid].keys():
                    host_name = self.change_of_placements[sid]["host"]
                elif "new_host" in self.change_of_placements[sid].keys():
                    host_name = self.change_of_placements[sid]["new_host"]

                if host_name is not None:
                    host = self.hosts[host_name]
        else:
            for _, h in self.hosts.items():
                if h.has_server(_s_info):
                    host = h
                    break

        return host

    def update_server_placements(self, change_of_placements=None, sync=False):
        """Update hosts with the change of server placements.

        Update the available resources of host and NUMA if sync is True.
        """

        if change_of_placements is None:
            change_of_placements = self.change_of_placements

        for _, change in change_of_placements.items():
            if "new_host" in change and "old_host" in change:
                # Migration case

                old_host = self.hosts[change.get("old_host")]
                new_host = self.hosts[change.get("new_host")]

                s_info = change.get("info")
                old_info = old_host.get_server_info(s_info)

                if sync:
                    # Adjust available remaining amount.

                    old_flavor = self.get_flavor(old_info.get("flavor_id"))
                    new_flavor = self.get_flavor(s_info.get("flavor_id"))

                    if new_flavor is None or old_flavor is None:
                        # NOTE(Gueyoung): ignore at this time.
                        # return False
                        pass
                    else:
                        s_info["vcpus"] = new_flavor.vCPUs
                        s_info["mem"] = new_flavor.mem_cap
                        s_info["disk"] = new_flavor.disk_cap

                        new_host.deduct_avail_resources(s_info)

                        if new_flavor.need_numa_alignment():
                            cell = new_host.NUMA.deduct_server_resources(s_info)
                            s_info["numa"] = cell

                        old_info["vcpus"] = old_flavor.vCPUs
                        old_info["mem"] = old_flavor.mem_cap
                        old_info["disk"] = old_flavor.disk_cap

                        old_host.rollback_avail_resources(old_info)

                        if old_flavor.need_numa_alignment():
                            old_host.NUMA.rollback_server_resources(old_info)

                old_host.remove_server(old_info)

                new_host.add_server(old_info)
                new_host.update_server(s_info)

                self.mark_host_updated(change.get("new_host"))
                self.mark_host_updated(change.get("old_host"))

            elif "new_host" in change and "old_host" not in change:
                # New server case

                host = self.hosts[change.get("new_host")]
                s_info = change.get("info")

                flavor = self.get_flavor(s_info.get("flavor_id"))

                if flavor is None:
                    # NOTE(Gueyoung): ignore at this time.
                    # return False
                    pass
                else:
                    s_info["vcpus"] = flavor.vCPUs
                    s_info["mem"] = flavor.mem_cap
                    s_info["disk"] = flavor.disk_cap

                    host.deduct_avail_resources(s_info)

                host.add_server(s_info)

                if sync:
                    if flavor is not None:
                        # Adjust available remaining amount.
                        if flavor.need_numa_alignment():
                            host.NUMA.deduct_server_resources(s_info)
                else:
                    if s_info.get("numa") != "none":
                        host.NUMA.add_server(s_info)

                self.mark_host_updated(change.get("new_host"))

            elif "new_host" not in change and "old_host" in change:
                # Deletion case

                host = self.hosts[change.get("old_host")]
                s_info = change.get("info")

                flavor = self.get_flavor(s_info.get("flavor_id"))

                if flavor is None:
                    # NOTE(Gueyoung): ignore at this time.
                    # return False
                    pass
                else:
                    s_info["vcpus"] = flavor.vCPUs
                    s_info["mem"] = flavor.mem_cap
                    s_info["disk"] = flavor.disk_cap

                    host.rollback_avail_resources(s_info)

                    if flavor.need_numa_alignment():
                        host.NUMA.rollback_server_resources(s_info)

                host.remove_server(s_info)

                self.mark_host_updated(change.get("old_host"))

            else:
                # Update case

                host = self.hosts[change.get("host")]
                s_info = change.get("info")

                if sync:
                    # Adjust available remaining amount.

                    old_info = host.get_server_info(s_info)

                    if s_info["flavor_id"] != old_info["flavor_id"]:
                        old_flavor = self.get_flavor(old_info.get("flavor_id"))
                        new_flavor = self.get_flavor(s_info.get("flavor_id"))

                        if old_flavor is None or new_flavor is None:
                            # NOTE(Gueyoung): ignore at this time.
                            # return False
                            pass
                        else:
                            host.rollback_avail_resources(old_info)

                            if old_flavor.need_numa_alignment():
                                host.NUMA.rollback_server_resources(old_info)

                            s_info["vcpus"] = new_flavor.vCPUs
                            s_info["mem"] = new_flavor.mem_cap
                            s_info["disk"] = new_flavor.disk_cap

                            host.deduct_avail_resources(s_info)

                            if new_flavor.need_numa_alignment():
                                cell = host.NUMA.deduct_server_resources(s_info)
                                s_info["numa"] = cell

                new_info = host.update_server(s_info)

                if new_info is not None:
                    self.mark_host_updated(change.get("host"))

        return True

    def update_server_grouping(self, change_of_placements=None, new_groups=None):
        """Update group member_hosts and hosts' memberships

        Caused by server addition, deletion, and migration.
        """

        if change_of_placements is None:
            change_of_placements = self.change_of_placements

        if new_groups is None:
            new_groups = self._get_new_grouping()

        for _, placement in change_of_placements.items():
            if "new_host" in placement.keys() and "old_host" in placement.keys():
                # Migrated server. This server can be unknown one previously.

                old_host = self.hosts[placement.get("old_host")]
                new_host = self.hosts[placement.get("new_host")]
                s_info = placement.get("info")
                new_info = new_host.get_server_info(s_info)

                # A list of Valet groups
                group_list = []
                self.get_groups_of_server(old_host, new_info, group_list)

                _group_list = self._get_groups_of_server(new_info, new_groups)
                for gk in _group_list:
                    if gk not in group_list:
                        group_list.append(gk)

                self._remove_server_from_groups(old_host, new_info)

                self._add_server_to_groups(new_host, new_info, group_list)

            elif "new_host" in placement.keys() and "old_host" not in placement.keys():
                # New server

                new_host = self.hosts[placement.get("new_host")]
                s_info = placement.get("info")
                new_s_info = new_host.get_server_info(s_info)

                group_list = self._get_groups_of_server(new_s_info, new_groups)

                self._add_server_to_groups(new_host, new_s_info, group_list)

            elif "new_host" not in placement.keys() and "old_host" in placement.keys():
                # Deleted server. This server can be unknown one previously.

                # Enabled host
                host = self.hosts[placement["old_host"]]

                self._remove_server_from_groups(host, placement.get("info"))

            else:
                host_name = placement.get("host")
                s_info = placement.get("info")

                if host_name in self.hosts.keys():
                    host = self.hosts[host_name]
                    new_info = host.get_server_info(s_info)

                    if new_info is not None:
                        self._update_server_in_groups(host, new_info)

        # To create, delete, and update dynamic Host-Aggregates.
        # TODO(Gueyoung): return error if fail to connect to Nova.
        self._manage_dynamic_host_aggregates()

    def _get_new_grouping(self, change_of_placements=None):
        """Verify and get new hosts' memberships."""

        if change_of_placements is None:
            change_of_placements = self.change_of_placements

        new_groups = {}

        # TODO: grouping verification for 'new' servers.
        # by calling verify_pre_valet_placements()
        # Should add each host's new memberships.

        # Add host's memberships for server-group.
        # Do not need to verify.
        for _, placement in change_of_placements.items():
            if "new_host" in placement.keys():
                host = self.hosts[placement.get("new_host")]
                s_info = placement.get("info")
                new_info = host.get_server_info(s_info)

                for gk, g in self.groups.items():
                    if g.factory == "server-group" and g.status == "enabled":
                        if g.has_server_uuid(new_info.get("uuid")):
                            if gk not in host.memberships.keys():
                                host.memberships[gk] = g
                                self.mark_host_updated(host.name)

                            if gk not in new_groups.keys():
                                new_groups[gk] = []
                            new_groups[gk].append(new_info)

        return new_groups

    def _get_groups_of_server(self, _s_info, new_groups):
        """Check and return group list where server belongs to."""

        group_list = []

        _stack_id = _s_info.get("stack_id")
        _stack_name = _s_info.get("stack_name")
        _uuid = _s_info.get("uuid")
        _name = _s_info.get("name")

        for gk, server_list in new_groups.items():
            for s_info in server_list:
                if s_info["uuid"] != "none":
                    if s_info["uuid"] == _uuid:
                        if gk not in group_list:
                            group_list.append(gk)
                        break

                if s_info["name"] != "none":
                    if s_info["stack_id"] != "none":
                        if s_info["stack_id"] == _stack_id and \
                           s_info["name"] == _name:
                            if gk not in group_list:
                                group_list.append(gk)
                            break

                    if s_info["stack_name"] != "none":
                        if s_info["stack_name"] == _stack_name and \
                           s_info["name"] == _name:
                            if gk not in group_list:
                                group_list.append(gk)
                            break

        return group_list

    def get_groups_of_server(self, _host, _s_info, _group_list):
        """Get groups where the server is assigned."""

        for gk in _host.memberships.keys():
            if gk not in self.groups.keys() or self.groups[gk].status != "enabled":
                del _host.memberships[gk]
                if isinstance(_host, Host):
                    self.mark_host_updated(_host.name)
                elif isinstance(_host, HostGroup):
                    self.mark_host_group_updated(_host.name)
                else:
                    self.mark_datacenter_updated()
                continue

            g = self.groups[gk]

            if g.factory not in ("valet", "server-group"):
                continue

            if isinstance(_host, HostGroup):
                if g.level != _host.host_type:
                    continue

            if g.has_server_in_host(_host.name, _s_info):
                if gk not in _group_list:
                    _group_list.append(gk)

        if isinstance(_host, Host) and _host.host_group is not None:
            if _host.host_group.is_available():
                self.get_groups_of_server(_host.host_group, _s_info, _group_list)
        elif isinstance(_host, HostGroup) and _host.parent_resource is not None:
            if _host.parent_resource.is_available():
                if isinstance(_host.parent_resource, HostGroup):
                    self.get_groups_of_server(_host.parent_resource, _s_info, _group_list)

    def _add_server_to_groups(self, _host, _s_info, _groups):
        """Add new server into groups."""

        for gk in _groups:
            # The group must be verified for host membership
            if gk not in _host.memberships.keys():
                continue

            if gk not in self.groups.keys() or self.groups[gk].status != "enabled":
                del _host.memberships[gk]
                if isinstance(_host, Host):
                    self.mark_host_updated(_host.name)
                elif isinstance(_host, HostGroup):
                    self.mark_host_group_updated(_host.name)
                else:
                    self.mark_datacenter_updated()
                continue

            g = self.groups[gk]

            if g.factory not in ("valet", "server-group"):
                continue

            if isinstance(_host, HostGroup):
                if g.level != _host.host_type:
                    continue

            if g.factory == "server-group":
                g.clean_server(_s_info["uuid"], _host.name)

            if g.add_server(_s_info, _host.name):
                g.updated = True
            else:
                self.logger.warning("server already exists in group")

        if isinstance(_host, Host) and _host.host_group is not None:
            if _host.host_group.is_available():
                self._add_server_to_groups(_host.host_group, _s_info, _groups)
        elif isinstance(_host, HostGroup) and _host.parent_resource is not None:
            if _host.parent_resource.is_available():
                if isinstance(_host.parent_resource, HostGroup):
                    self._add_server_to_groups(_host.parent_resource, _s_info, _groups)

    def _remove_server_from_groups(self, _host, _s_info):
        """Remove server from related groups."""

        for gk in _host.memberships.keys():
            if gk not in self.groups.keys() or self.groups[gk].status != "enabled":
                del _host.memberships[gk]

                if isinstance(_host, Host):
                    self.mark_host_updated(_host.name)
                elif isinstance(_host, HostGroup):
                    self.mark_host_group_updated(_host.name)
                else:
                    self.mark_datacenter_updated()
                continue

            g = self.groups[gk]

            if g.factory not in ("valet", "server-group"):
                continue

            if isinstance(_host, HostGroup):
                if g.level != _host.host_type:
                    continue

            if g.remove_server(_s_info):
                g.updated = True

            if g.remove_server_from_host(_host.name, _s_info):
                g.updated = True

            # Remove host from group's membership if the host has no servers of the group.
            if g.remove_member(_host.name):
                g.updated = True

            # Remove group from host's membership if group does not have the host
            # Not consider group has datacenter level.
            if isinstance(_host, Host) or isinstance(_host, HostGroup):
                if _host.remove_membership(g):
                    if isinstance(_host, Host):
                        self.mark_host_updated(_host.name)
                    elif isinstance(_host, HostGroup):
                        self.mark_host_group_updated(_host.name)
                    else:
                        self.mark_datacenter_updated()

            if len(g.server_list) == 0:
                g.status = "disabled"
                g.updated = True

        if isinstance(_host, Host) and _host.host_group is not None:
            if _host.host_group.is_available():
                self._remove_server_from_groups(_host.host_group, _s_info)
        elif isinstance(_host, HostGroup) and _host.parent_resource is not None:
            if _host.parent_resource.is_available():
                if isinstance(_host.parent_resource, HostGroup):
                    self._remove_server_from_groups(_host.parent_resource, _s_info)

    def _update_server_in_groups(self, _host, _s_info):
        """Update server info in groups."""

        for gk in _host.memberships.keys():
            if gk not in self.groups.keys() or self.groups[gk].status != "enabled":
                del _host.memberships[gk]
                if isinstance(_host, Host):
                    self.mark_host_updated(_host.name)
                elif isinstance(_host, HostGroup):
                    self.mark_host_group_updated(_host.name)
                else:
                    self.mark_datacenter_updated()
                continue

            g = self.groups[gk]

            if g.factory not in ("valet", "server-group"):
                continue

            if isinstance(_host, HostGroup):
                if g.level != _host.host_type:
                    continue

            if g.update_server(_s_info):
                g.update_server_in_host(_host.name, _s_info)
                g.updated = True

        if isinstance(_host, Host) and _host.host_group is not None:
            if _host.host_group.is_available():
                self._update_server_in_groups(_host.host_group, _s_info)
        elif isinstance(_host, HostGroup) and _host.parent_resource is not None:
            if _host.parent_resource.is_available():
                if isinstance(_host.parent_resource, HostGroup):
                    self._update_server_in_groups(_host.parent_resource, _s_info)

    def add_group(self, _g_name, _g_type, _level, _factory, _host_name):
        """Add/Enable group unless the group exists or disabled."""

        if _g_name not in self.groups.keys():
            group = Group(_g_name)
            group.group_type = _g_type
            group.factory = _factory
            group.level = _level
            group.rule = self._get_rule_of_group(_g_name)
            group.new = True
            group.updated = True
            self.groups[_g_name] = group
        elif self.groups[_g_name].status != "enabled":
            self.groups[_g_name].status = "enabled"
            self.groups[_g_name].updated = True

        if _host_name in self.hosts.keys():
            host = self.hosts[_host_name]
        else:
            host = self.host_groups[_host_name]

        # Update host memberships.
        if host is not None:
            if _g_name not in host.memberships.keys():
                host.memberships[_g_name] = self.groups[_g_name]

                if isinstance(host, Host):
                    self.mark_host_updated(_host_name)
                elif isinstance(host, HostGroup):
                    self.mark_host_group_updated(_host_name)

        return True

    def _get_rule_of_group(self, _gk):
        """Get valet group rule of the given group."""

        rule_name_elements = _gk.split(':')
        rule_name = rule_name_elements[len(rule_name_elements)-1]

        if rule_name in self.group_rules.keys():
            return self.group_rules[rule_name]

        return None

    def get_group_by_uuid(self, _uuid):
        """Check and get the group with its uuid."""

        for _, g in self.groups.items():
            if g.uuid == _uuid:
                return g

        return None

    def check_valid_rules(self, _tenant_id, _rule_list, use_ex=True):
        """Check if given rules are valid to be used."""

        for rk in _rule_list:
            if rk not in self.group_rules.keys():
                return "not exist rule (" + rk + ")"

            # TODO(Gueyoung): if disabled,
            # what to do with placed servers under this rule?
            if self.group_rules[rk].status != "enabled":
                return "rule (" + rk + ") is not enabled"

            if not use_ex:
                if self.group_rules[rk].rule_type == "exclusivity":
                    return "exclusivity not supported"

            rule = self.group_rules[rk]
            if len(rule.members) > 0 and _tenant_id not in rule.members:
                return "no valid tenant to use rule (" + rk + ")"

        return "ok"

    def _manage_dynamic_host_aggregates(self):
        """Create, delete, or update Host-Aggregates after placement decisions."""

        for gk in self.groups.keys():
            g = self.groups[gk]
            if g.group_type == "exclusivity" and g.status == "enabled":
                aggr_name = "valet:" + g.name
                if aggr_name not in self.groups.keys():
                    # Create Host-Aggregate.
                    status = self._add_exclusivity_aggregate(aggr_name, g)
                    # TODO(Gueyoung): return error
                    if status != "ok":
                        self.logger.warning("error while adding dynamic host-aggregate")
                else:
                    dha = self.groups[aggr_name]
                    for hk in g.member_hosts.keys():
                        if hk not in dha.member_hosts.keys():
                            # Add new host into Host-Aggregate.
                            status = self._update_exclusivity_aggregate(dha,
                                                                        self.hosts[hk])
                            # TODO(Gueyoung): return error
                            if status != "ok":
                                self.logger.warning("error while updating dynamic host-aggregate")

        for gk in self.groups.keys():
            g = self.groups[gk]
            if g.group_type == "aggr" and g.status == "enabled":
                if g.name.startswith("valet:"):
                    if g.metadata["valet_type"] == "exclusivity":
                        name_elements = g.name.split(':', 1)
                        ex_group_name = name_elements[1]
                        if ex_group_name not in self.groups.keys() or \
                           self.groups[ex_group_name].status != "enabled":
                            # Delete Host-Aggregate
                            status = self._remove_exclusivity_aggregate(g)
                            # TODO(Gueyoung): return error
                            if status != "ok":
                                self.logger.warning("error while removing dynamic host-aggregate")
                        else:
                            ex_group = self.groups[ex_group_name]
                            for hk in g.member_hosts.keys():
                                if hk not in ex_group.member_hosts.keys():
                                    # Remove host from Host-Aggregate.
                                    status = self._remove_host_from_exclusivity_aggregate(g,
                                                                                          self.hosts[hk])

                                    # TODO(Gueyoung): return error
                                    if status != "ok":
                                        self.logger.warning("error while removing host from dynamic host-aggregate")

    def _add_exclusivity_aggregate(self, _name, _group):
        """Create platform Host-Aggregate for Valet rules.

           Exclusivity: create Host-Aggregate, and lock.
        """

        group = Group(_name)
        group.group_type = "aggr"
        group.level = "host"
        group.factory = "nova"

        metadata = {"valet_type": "exclusivity"}

        new_host_list = []
        ex_metadata = {}

        for hk in _group.member_hosts.keys():
            host = self.hosts[hk]
            aggregates = host.get_aggregates()

            old_aggregates = []
            for a in aggregates:
                if a.name.startswith("valet:"):
                    continue

                for mk, mv in a.metadata.items():
                    if mk not in ex_metadata.keys():
                        ex_metadata[mk] = mv
                    else:
                        if isinstance(ex_metadata[mk], list):
                            if mv not in ex_metadata[mk]:
                                ex_metadata[mk].append(mv)
                                self.logger.warning("multiple values of metadata key")
                        else:
                            if mv != ex_metadata[mk]:
                                value_list = [ex_metadata[mk], mv]
                                ex_metadata[mk] = value_list
                                self.logger.warning("multiple values of metadata key")

                old_aggregates.append(a)

                if hk in a.member_hosts.keys():
                    del a.member_hosts[hk]
                    a.updated = True

                if a.name in host.memberships.keys():
                    del host.memberships[a.name]

            if len(old_aggregates) > 0:
                metadata[hk] = str(old_aggregates[0].uuid)
                for i in range(1, len(old_aggregates)):
                    metadata[hk] += ("," + str(old_aggregates[i].uuid))

            new_host_list.append(host)

        metadata["prior_metadata"] = ex_metadata

        group.metadata = metadata

        for host in new_host_list:
            group.member_hosts[host.name] = []

            host.memberships[_name] = group
            self.mark_host_updated(host.name)

        group.updated = True

        if not self.metadata.source.valid_client(self.datacenter_url):
            self.metadata.source.set_client(self.datacenter_url)

        status = self.metadata.create_exclusive_aggregate(group,
                                                          new_host_list)

        self.groups[_name] = group

        return status

    def _update_exclusivity_aggregate(self, _group, _host):
        """Update platform Host-Aggregate for Valet rules.

           Exclusivity: update Host-Aggregate, and lock.
        """

        status = "ok"

        aggregates = _host.get_aggregates()

        if _group.group_type == "aggr":
            if _host.name not in _group.member_hosts.keys():
                old_aggregates = []
                ex_metadata = _group.metadata["prior_metadata"]

                for a in aggregates:
                    if a.name.startswith("valet:"):
                        continue

                    for mk, mv in a.metadata.items():
                        if mk not in ex_metadata.keys():
                            ex_metadata[mk] = mv
                        else:
                            if isinstance(ex_metadata[mk], list):
                                if mv not in ex_metadata[mk]:
                                    ex_metadata[mk].append(mv)
                                    self.logger.warning("multiple values of metadata key")
                            else:
                                if mv != ex_metadata[mk]:
                                    value_list = [ex_metadata[mk], mv]
                                    ex_metadata[mk] = value_list
                                    self.logger.warning("multiple values of metadata key")

                    old_aggregates.append(a)

                    if _host.name in a.member_hosts.keys():
                        del a.member_hosts[_host.name]
                        a.updated = True

                    if a.name in _host.memberships.keys():
                        del _host.memberships[a.name]

                if len(old_aggregates) > 0:
                    _group.metadata[_host.name] = str(old_aggregates[0].uuid)
                    for i in range(1, len(old_aggregates)):
                        _group.metadata[_host.name] += ("," + str(old_aggregates[i].uuid)) 

                _group.metadata["prior_metadata"] = ex_metadata

                _group.member_hosts[_host.name] = []
                _group.updated = True

                _host.memberships[_group.name] = _group
                self.mark_host_updated(_host.name)

                if not self.metadata.source.valid_client(self.datacenter_url):
                    self.metadata.source.set_client(self.datacenter_url)

                status = self.metadata.update_exclusive_aggregate(_group.uuid,
                                                                  _group.metadata,
                                                                  _host.name,
                                                                  old_aggregates)

        return status

    def _remove_exclusivity_aggregate(self, _group):
        """Remove dynamic Host-Aggregate."""

        for hk in _group.member_hosts.keys():
            host = self.hosts[hk]

            status = self._remove_host_from_exclusivity_aggregate(_group, host)
            if status != "ok":
                self.logger.warning("error while removing host from dynamic host-aggregate")

        del self.groups[_group.name]

        if not self.metadata.source.valid_client(self.datacenter_url):
            self.metadata.source.set_client(self.datacenter_url)

        return self.metadata.remove_exclusive_aggregate(_group.uuid)

    def _remove_host_from_exclusivity_aggregate(self, _group, _host):
        """Update platform Host-Aggregate for Valet rules.

           Exclusivity: delete host from dynamic Host-Aggregate.
        """

        status = "ok"

        if _group.group_type == "aggr":
            if _host.name in _group.member_hosts.keys():
                old_aggregates = []
                if _host.name in _group.metadata.keys():
                    aggr_ids = _group.metadata[_host.name].split(',')

                    for aid in aggr_ids:
                        aggr = self.get_group_by_uuid(int(aid))
                        if aggr is not None:
                            aggr.member_hosts[_host.name] = []
                            aggr.updated = True
                            old_aggregates.append(aggr)

                            if aggr.name not in _host.memberships.keys():
                                _host.memberships[aggr.name] = aggr

                    _group.metadata[_host.name] = "" 

                del _group.member_hosts[_host.name]
                _group.updated = True

                del _host.memberships[_group.name]
                self.mark_host_updated(_host.name)

                if not self.metadata.source.valid_client(self.datacenter_url):
                    self.metadata.source.set_client(self.datacenter_url)

                status = self.metadata.remove_host_from_exclusive_aggregate(_group.uuid,
                                                                            _group.metadata,
                                                                            _host.name,
                                                                            old_aggregates)

        return status

    def sync_with_platform(self, store=False):
        """Communicate with platform (e.g., nova) to get resource status.

        Due to dependencies between resource types,
        keep the following order of process.
        """

        if len(self.pending_requests) > 0:
            return True

        self.logger.info("load data from platform (e.g., nova)")

        # Set the platorm client lib (e.g., novaclient).
        if not self.metadata.source.valid_client(self.datacenter_url):
            count = 0
            while count < 3:
                if not self.metadata.source.set_client(self.datacenter_url):
                    self.logger.warning("fail to set novaclient: try again")
                    count += 1
                    time.sleep(1)
                else:
                    break
            if count == 3:
                self.logger.error("fail to set novaclient")
                return False

        count = 0
        while count < 3:
            # Set each flavor and its metadata.
            if not self.metadata.get_flavors(self):
                self.logger.warning("fail to get flavors: try again")
                count += 1
                time.sleep(1)
            else:
                break
        if count == 3:
            self.logger.error("fail to get flavors")
            return False

        count = 0
        while count < 3:
            # Set each compute host and servers information.
            if not self.compute.get_hosts(self):
                self.logger.warning("fail to get hosts: try again")
                count += 1
                time.sleep(1)
            else:
                break
        if count == 3:
            self.logger.error("fail to get hosts")
            return False

        # TODO(Gueyoung): need to every time?
        # Set the layout between each compute host and rack.
        if not self.topology.get_topology(self):
            return False

        count = 0
        while count < 3:
            # Set the availability-zone, host-aggregate, and server-group
            # of each compute host.
            if not self.metadata.get_groups(self):
                self.logger.warning("fail to get groups: try again")
                count += 1
                time.sleep(1)
            else:
                break
        if count == 3:
            self.logger.error("fail to get groups")
            return False

        # Update total capacities of each host.
        # Triggered by overcommit ratio update or newly added.
        for _, host in self.hosts.items():
            if host.is_available() and host.updated:
                self.compute_resources(host)

        # Update server placements in hosts
        # If sync is True, update the available capacities.
        if not self.update_server_placements(sync=True):
            return False

        # Update the available capacities of each NUMA and host.
        # Triggered by unknown server additions and deletions.
        for _, host in self.hosts.items():
            if host.is_available() and host.updated:
                self.compute_avail_resources(host)

        # Update server grouping changed by deletion and migration of servers.
        # TODO(Gueyoung): return False if fail to connect to Nova.
        self.update_server_grouping()

        # Update racks (and clusters) and datacenter based on host change.
        self.update_resource()

        # TODO: If peoridic batches to collect data from platform is activated,
        # should check if there is any update before storing data into DB.
        if store:
            self.store_resource()

        return True

    def get_flavor(self, _id):
        """Get a flavor info."""

        if isinstance(_id, six.string_types):
            flavor_id = _id
        else:
            flavor_id = str(_id)

        self.logger.debug("fetching flavor = " + flavor_id)

        flavor = None
        if flavor_id in self.flavors.keys():
            flavor = self.flavors[flavor_id]
        else:
            for _, f in self.flavors.items():
                if f.flavor_id == flavor_id:
                    flavor = f
                    break

        if flavor is not None:
            # Check if detailed information.
            # TODO(Gueyoung): what if flavor specs changed from platform?
            if flavor.vCPUs == 0:
                if not self.metadata.source.valid_client(self.datacenter_url):
                    count = 0
                    while count < 3:
                        if not self.metadata.source.set_client(self.datacenter_url):
                            self.logger.warning("fail to set novaclient: try again")
                            count += 1
                            time.sleep(1)
                        else:
                            break
                    if count == 3:
                        self.logger.error("fail to set novaclient")
                        return None

                f = self.metadata.source.get_flavor(flavor.flavor_id)
                if f is None:
                    flavor = None
                else:
                    flavor.set_info(f)
                    flavor.updated = True

                    self.logger.debug("flavor (" + flavor.name + ") fetched")
        else:
            self.logger.warning("unknown flavor = " + flavor_id)

        return flavor

    def store_resource(self, opt=None, req_id=None):
        """Store resource status into DB."""

        flavor_updates = {}
        group_updates = {}
        host_updates = {}
        host_group_updates = {}

        # Do not store disbaled resources.

        for fk, flavor in self.flavors.items():
            # TODO(Gueyoung): store disabled flavor?
            flavor_updates[fk] = flavor.get_json_info()

        for gk, group in self.groups.items():
            if group.status == "enabled":
                if group.factory != "valet":
                    group_updates[gk] = group.get_json_info()

        for hk, host in self.hosts.items():
            if host.is_available():
                host_updates[hk] = host.get_json_info()

        for hgk, host_group in self.host_groups.items():
            if host_group.is_available():
                host_group_updates[hgk] = host_group.get_json_info()

        datacenter_update = self.datacenter.get_json_info()

        # If there is pending requests (i.e., not confirmed nor rollbacked),
        # do NOT sync with platform when dealing with new request.
        # Here, add/remove request from/to pending list
        # to track the list of pending requests. 
        if opt is not None and req_id is not None:
            if opt in ("create", "delete", "update"):
                self.pending_requests.append(req_id)
            elif opt in ("confirm", "rollback"):
                for rid in self.pending_requests:
                    if rid == req_id:
                        self.pending_requests.remove(rid)
                        break

        json_update = {'flavors': flavor_updates, 'groups': group_updates, 'hosts': host_updates,
                       'host_groups': host_group_updates, 'datacenter': datacenter_update}

        if self.new:
            if not self.dbh.create_resource(self.datacenter_id,
                                            self.datacenter_url,
                                            self.pending_requests,
                                            json_update):
                return False
        else:
            if not self.dbh.update_resource(self.datacenter_id,
                                            self.datacenter_url,
                                            self.pending_requests,
                                            json_update):
                return False

        if self.new:
            self.logger.debug("new datacenter = " + self.datacenter_id)
            self.logger.debug("    url = " + self.datacenter_url)
        else:
            self.logger.debug("updated datacenter = " + self.datacenter_id)
            self.logger.debug("        url = " + self.datacenter_url)
        self.logger.debug("region = " + json.dumps(json_update['datacenter'], indent=4))
        self.logger.debug("racks = " + json.dumps(json_update['host_groups'], indent=4))
        self.logger.debug("hosts = " + json.dumps(json_update['hosts'], indent=4))
        self.logger.debug("groups = " + json.dumps(json_update['groups'], indent=4))
        self.logger.debug("flavors = ")
        for fk, f_info in json_update['flavors'].items():
            if f_info["vCPUs"] > 0:
                self.logger.debug(json.dumps(f_info, indent=4))

        updated_valet_groups = {}
        new_valet_groups = {}
        deleted_valet_groups = {}
        for gk, group in self.groups.items():
            if group.status == "enabled":
                if group.factory == "valet":
                    if group.new:
                        new_valet_groups[gk] = group.get_json_info()
                    elif group.updated:
                        updated_valet_groups[gk] = group.get_json_info()
            else:
                if group.factory == "valet":
                    deleted_valet_groups[gk] = group.get_json_info()

        for gk, g_info in new_valet_groups.items():
            if not self.dbh.create_valet_group(gk, g_info):
                return False

            self.logger.debug("new valet group = " + gk)
            self.logger.debug("info = " + json.dumps(g_info, indent=4))

        for gk, g_info in updated_valet_groups.items():
            if not self.dbh.update_valet_group(gk, g_info):
                return False

            self.logger.debug("updated valet group = " + gk)
            self.logger.debug("info = " + json.dumps(g_info, indent=4))

        for gk, g_info in deleted_valet_groups.items():
            if not self.dbh.delete_valet_group(gk):
                return False

            self.logger.debug("deleted valet group = " + gk)
            self.logger.debug("info = " + json.dumps(g_info, indent=4))

        return True
