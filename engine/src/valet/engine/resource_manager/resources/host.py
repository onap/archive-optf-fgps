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


class Host(object):
    """Container for compute host."""

    def __init__(self, _name):
        """Define compute host."""

        self.name = _name

        self.uuid = None

        self.status = "enabled"
        self.state = "up"

        # Enabled group objects (e.g., aggregate) this hosting server is in
        self.memberships = {}

        self.vCPUs = 0
        self.original_vCPUs = 0
        self.avail_vCPUs = 0

        self.mem_cap = 0   # MB
        self.original_mem_cap = 0
        self.avail_mem_cap = 0

        self.local_disk_cap = 0    # GB, ephemeral
        self.original_local_disk_cap = 0
        self.avail_local_disk_cap = 0

        self.vCPUs_used = 0
        self.free_mem_mb = 0
        self.free_disk_gb = 0
        self.disk_available_least = 0

        # To track available cores and memory per NUMA cell
        self.NUMA = NUMA()

        self.host_group = None    # host_group object (e.g., rack)

        # Kepp a list of placed servers' information
        # Here, server_info including {uuid, orch_id, name,
        #                              stack_id, stack_name,
        #                              flavor_id, image_id, tenent_id,
        #                              vcpus, mem, disk, numa,
        #                              state, status}
        self.server_list = []

        # If this host is not defined yet (unknown host).
        self.candidate_host_types = {}

        self.updated = False

    def is_available(self):
        """Check if host is available."""

        if self.status == "enabled" and self.state == "up":
            return True
        else:
            return False

    def has_server(self, _s_info):
        """Check if server is located in this host."""

        for s_info in self.server_list:
            if _s_info["uuid"] != "none":
                if s_info["uuid"] != "none" and \
                   s_info["uuid"] == _s_info["uuid"]:
                    return True

            if _s_info["stack_id"] != "none":
                if (s_info["stack_id"] != "none" and \
                    s_info["stack_id"] == _s_info["stack_id"]) and \
                   s_info["name"] == _s_info["name"]:
                    return True

            if _s_info["stack_name"] != "none":
                if (s_info["stack_name"] != "none" and \
                    s_info["stack_name"] == _s_info["stack_name"]) and \
                   s_info["name"] == _s_info["name"]:
                    return True

        return False

    def get_server_info(self, _s_info):
        """Get server info."""

        for s_info in self.server_list:
            if _s_info["uuid"] != "none":
                if s_info["uuid"] != "none" and \
                   s_info["uuid"] == _s_info["uuid"]:
                    return s_info

            if _s_info["stack_id"] != "none":
                if (s_info["stack_id"] != "none" and \
                    s_info["stack_id"] == _s_info["stack_id"]) and \
                   s_info["name"] == _s_info["name"]:
                    return s_info

            if _s_info["stack_name"] != "none":
                if (s_info["stack_name"] != "none" and \
                    s_info["stack_name"] == _s_info["stack_name"]) and \
                   s_info["name"] == _s_info["name"]:
                    return s_info

        return None

    def add_server(self, _s_info):
        """Add new server to this host."""

        self.server_list.append(_s_info)

    def remove_server(self, _s_info):
        """Remove server from this host."""

        for s_info in self.server_list:
            if _s_info["uuid"] != "none":
                if s_info["uuid"] != "none" and \
                   s_info["uuid"] == _s_info["uuid"]:
                    self.server_list.remove(s_info)
                    return True

            if _s_info["stack_id"] != "none":
                if (s_info["stack_id"] != "none" and \
                    s_info["stack_id"] == _s_info["stack_id"]) and \
                   s_info["name"] == _s_info["name"]:
                    self.server_list.remove(s_info)
                    return True

            if _s_info["stack_name"] != "none":
                if (s_info["stack_name"] != "none" and \
                    s_info["stack_name"] == _s_info["stack_name"]) and \
                   s_info["name"] == _s_info["name"]:
                    self.server_list.remove(s_info)
                    return True

        return False

    def update_server(self, _s_info):
        """Update server with info from given info.

        The info comes from platform or request (e.g., Heat stack).
        """

        updated = None

        s_info = self.get_server_info(_s_info)

        if s_info is not None:
            if _s_info["stack_id"] != "none" and \
               _s_info["stack_id"] != s_info["stack_id"]:
                s_info["stack_id"] = _s_info["stack_id"]
                updated = s_info

            if _s_info["uuid"] != "none" and \
               _s_info["uuid"] != s_info["uuid"]:
                s_info["uuid"] = _s_info["uuid"]
                updated = s_info

            if _s_info["flavor_id"] != "none" and \
               _s_info["flavor_id"] != s_info["flavor_id"]:
                s_info["flavor_id"] = _s_info["flavor_id"]
                updated = s_info

            if _s_info["vcpus"] != -1 and \
               _s_info["vcpus"] != s_info["vcpus"]:
                s_info["vcpus"] = _s_info["vcpus"]
                updated = s_info

            if _s_info["mem"] != -1 and \
               _s_info["mem"] != s_info["mem"]:
                s_info["mem"] = _s_info["mem"]
                updated = s_info

            if _s_info["disk"] != -1 and \
               _s_info["disk"] != s_info["disk"]:
                s_info["disk"] = _s_info["disk"]
                updated = s_info

            if _s_info["image_id"] != "none" and \
               _s_info["image_id"] != s_info["image_id"]:
                s_info["image_id"] = _s_info["image_id"]
                updated = s_info

            if _s_info["state"] != "none" and \
               _s_info["state"] != s_info["state"]:
                s_info["state"] = _s_info["state"]
                updated = s_info

            if _s_info["status"] != "none" and \
               _s_info["status"] != s_info["status"]:
                s_info["status"] = _s_info["status"]
                updated = s_info

            if _s_info["numa"] != "none" and \
               _s_info["numa"] != s_info["numa"]:
                s_info["numa"] = _s_info["numa"]
                updated = s_info

            if updated is not None:
                cell = self.NUMA.pop_cell_of_server(updated)

                if updated["numa"] == "none":
                    if cell != "none":
                        updated["numa"] = cell

                self.NUMA.add_server(updated)

        return updated

    def remove_membership(self, _g):
        """Remove a membership.

        To return to the resource pool for other placements.
        """

        if _g.factory in ("valet", "server-group"):
            if self.name not in _g.member_hosts.keys():
                del self.memberships[_g.name]

                return True

        return False

    def compute_cpus(self, _overcommit_ratio):
        """Compute and init oversubscribed CPUs."""

        if self.vCPUs == 0:
            # New host case

            self.vCPUs = self.original_vCPUs * _overcommit_ratio
            self.avail_vCPUs = self.vCPUs
            self.NUMA.init_cpus(self.vCPUs)
        else:
            vcpus = self.original_vCPUs * _overcommit_ratio

            if vcpus != self.vCPUs:
                # Change of overcommit_ratio

                self.NUMA.adjust_cpus(self.vCPUs, vcpus)

                used = self.vCPUs - self.avail_vCPUs

                self.vCPUs = vcpus
                self.avail_vCPUs = self.vCPUs - used

    def compute_avail_cpus(self):
        """Compute available CPUs after placements."""

        avail_vcpus = self.vCPUs - self.vCPUs_used

        if avail_vcpus != self.avail_vCPUs:
            # Incurred due to unknown server placement.

            diff = self.avail_vCPUs - avail_vcpus
            self.NUMA.apply_unknown_cpus(diff)

            self.avail_vCPUs = avail_vcpus

            return "avail cpus changed (" + str(diff) + ") in " + self.name

        return "ok"

    def compute_mem(self, _overcommit_ratio):
        """Compute and init oversubscribed mem capacity."""

        if self.mem_cap == 0:
            # New host case

            self.mem_cap = self.original_mem_cap * _overcommit_ratio

            self.avail_mem_cap = self.mem_cap

            self.NUMA.init_mem(self.mem_cap)
        else:
            mem_cap = self.original_mem_cap * _overcommit_ratio

            if mem_cap != self.mem_cap:
                # Change of overcommit_ratio

                self.NUMA.adjust_mem(self.mem_cap, mem_cap)

                used = self.mem_cap - self.avail_mem_cap

                self.mem_cap = mem_cap
                self.avail_mem_cap = self.mem_cap - used

    def compute_avail_mem(self):
        """Compute available mem capacity after placements."""

        used_mem_mb = self.original_mem_cap - self.free_mem_mb

        avail_mem_cap = self.mem_cap - used_mem_mb

        if avail_mem_cap != self.avail_mem_cap:
            # Incurred due to unknown server placement.

            diff = self.avail_mem_cap - avail_mem_cap
            self.NUMA.apply_unknown_mem(diff)

            self.avail_mem_cap = avail_mem_cap

            return "avail mem changed(" + str(diff) + ") in " + self.name

        return "ok"

    def compute_disk(self, _overcommit_ratio):
        """Compute and init oversubscribed disk capacity."""

        if self.local_disk_cap == 0:
            # New host case

            self.local_disk_cap = self.original_local_disk_cap * _overcommit_ratio

            self.avail_local_disk_cap = self.local_disk_cap
        else:
            local_disk_cap = self.original_local_disk_cap * _overcommit_ratio

            if local_disk_cap != self.local_disk_cap:
                # Change of overcommit_ratio

                used = self.local_disk_cap - self.avail_local_disk_cap

                self.local_disk_cap = local_disk_cap
                self.avail_local_disk_cap = self.local_disk_cap - used

    def compute_avail_disk(self):
        """Compute available disk capacity after placements."""

        free_disk_cap = self.free_disk_gb
        if self.disk_available_least > 0:
            free_disk_cap = min(self.free_disk_gb, self.disk_available_least)

        used_disk_cap = self.original_local_disk_cap - free_disk_cap

        avail_local_disk_cap = self.local_disk_cap - used_disk_cap

        if avail_local_disk_cap != self.avail_local_disk_cap:
            diff = self.avail_local_disk_cap - avail_local_disk_cap

            self.avail_local_disk_cap = avail_local_disk_cap

            return "avail disk changed(" + str(diff) + ") in " + self.name

        return "ok"

    def deduct_avail_resources(self, _s_info):
        """Deduct available amount of resources of this host."""

        if _s_info.get("vcpus") != -1:
            self.avail_vCPUs -= _s_info.get("vcpus")
            self.avail_mem_cap -= _s_info.get("mem")
            self.avail_local_disk_cap -= _s_info.get("disk")

    def rollback_avail_resources(self, _s_info):
        """Rollback available amount of resources of this host."""

        if _s_info.get("vcpus") != -1:
            self.avail_vCPUs += _s_info.get("vcpus")
            self.avail_mem_cap += _s_info.get("mem")
            self.avail_local_disk_cap += _s_info.get("disk")

    def get_availability_zone(self):
        """Get the availability-zone of this host."""

        for gk, g in self.memberships.items():
            if g.group_type == "az":
                return g

        return None

    def get_aggregates(self):
        """Get the list of Host-Aggregates of this host."""

        aggregates = []

        for gk, g in self.memberships.items():
            if g.group_type == "aggr":
                aggregates.append(g)

        return aggregates

    def get_json_info(self):
        """Get compute host info as JSON format"""

        membership_list = []
        for gk in self.memberships.keys():
            membership_list.append(gk)

        return {'status': self.status, 'state': self.state,
                'uuid': self.uuid,
                'membership_list': membership_list,
                'vCPUs': self.vCPUs,
                'original_vCPUs': self.original_vCPUs,
                'avail_vCPUs': self.avail_vCPUs,
                'mem': self.mem_cap,
                'original_mem': self.original_mem_cap,
                'avail_mem': self.avail_mem_cap,
                'local_disk': self.local_disk_cap,
                'original_local_disk': self.original_local_disk_cap,
                'avail_local_disk': self.avail_local_disk_cap,
                'vCPUs_used': self.vCPUs_used,
                'free_mem_mb': self.free_mem_mb,
                'free_disk_gb': self.free_disk_gb,
                'disk_available_least': self.disk_available_least,
                'NUMA': self.NUMA.get_json_info(),
                'parent': self.host_group.name,
                'server_list': self.server_list,
                'candidate_host_types': self.candidate_host_types}
