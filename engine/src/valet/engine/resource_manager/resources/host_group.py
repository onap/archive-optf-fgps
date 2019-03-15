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
from valet.engine.app_manager.group import LEVEL


class HostGroup(object):
    """Container for host group (rack)."""

    def __init__(self, _id):
        self.name = _id

        self.status = "enabled"
        self.host_group = None

        # 'rack' or 'cluster' (e.g., power domain, zone)
        self.host_type = "rack"

        self.parent_resource = None   # e.g., datacenter object
        self.child_resources = {}    # e.g., hosting server objects

        # Enabled group objects (e.g., aggregate) in this group
        self.memberships = {}

        self.vCPUs = 0
        self.avail_vCPUs = 0

        self.mem_cap = 0   # MB
        self.avail_mem_cap = 0

        self.local_disk_cap = 0   # GB, ephemeral
        self.avail_local_disk_cap = 0

        # A list of placed servers' info
        self.server_list = []

        self.updated = False

    def is_available(self):
        if self.status == "enabled":
            return True
        else:
            return False

    def init_resources(self):
        self.vCPUs = 0
        self.avail_vCPUs = 0
        self.mem_cap = 0    # MB
        self.avail_mem_cap = 0
        self.local_disk_cap = 0    # GB, ephemeral
        self.avail_local_disk_cap = 0

    def init_memberships(self):
        for gk in self.memberships.keys():
            g = self.memberships[gk]

            if g.factory == "valet":
                if LEVEL.index(g.level) < LEVEL.index(self.host_type):
                    del self.memberships[gk]
            else:
                del self.memberships[gk]

    def remove_membership(self, _g):
        """Remove a membership. """

        if _g.factory == "valet":
            if self.name not in _g.member_hosts.keys():
                del self.memberships[_g.name]
                return True

        return False

    def get_json_info(self):
        membership_list = []
        for gk in self.memberships.keys():
            membership_list.append(gk)

        child_list = []
        for ck in self.child_resources.keys():
            child_list.append(ck)

        return {'status': self.status,
                'host_type': self.host_type,
                'membership_list': membership_list,
                'vCPUs': self.vCPUs,
                'avail_vCPUs': self.avail_vCPUs,
                'mem': self.mem_cap,
                'avail_mem': self.avail_mem_cap,
                'local_disk': self.local_disk_cap,
                'avail_local_disk': self.avail_local_disk_cap,
                'parent': self.parent_resource.name,
                'children': child_list,
                'server_list': self.server_list}
